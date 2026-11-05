import sqlite3
from pathlib import Path
from contextlib import contextmanager

# ==========================================
# DATABASE CONFIGURATION
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "jawad_ai.db"

DATA_DIR.mkdir(parents=True, exist_ok=True)


# ==========================================
# DATABASE CONNECTION
# ==========================================

@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def rows_to_dicts(rows):
    return [dict(row) for row in rows]


# ==========================================
# INITIALIZE DATABASE
# ==========================================

def init_db():
    with get_connection() as conn:

        conn.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(conversation_id)
                    REFERENCES conversations(id)
                    ON DELETE CASCADE
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT,
                memory TEXT NOT NULL,
                importance INTEGER DEFAULT 3,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                file_type TEXT,
                file_hash TEXT UNIQUE,
                status TEXT DEFAULT 'uploaded',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS document_chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER,
                chunk_index INTEGER,
                content TEXT NOT NULL,
                FOREIGN KEY(document_id)
                    REFERENCES documents(id)
                    ON DELETE CASCADE
            )
        """)

        conn.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts
            USING fts5(
                content,
                content='document_chunks',
                content_rowid='id'
            )
        """)

        conn.executescript("""
            CREATE TRIGGER IF NOT EXISTS chunks_ai
            AFTER INSERT ON document_chunks BEGIN
                INSERT INTO chunks_fts(rowid, content)
                VALUES (new.id, new.content);
            END;

            CREATE TRIGGER IF NOT EXISTS chunks_ad
            AFTER DELETE ON document_chunks BEGIN
                INSERT INTO chunks_fts(chunks_fts, rowid, content)
                VALUES ('delete', old.id, old.content);
            END;

            CREATE TRIGGER IF NOT EXISTS chunks_au
            AFTER UPDATE ON document_chunks BEGIN
                INSERT INTO chunks_fts(chunks_fts, rowid, content)
                VALUES ('delete', old.id, old.content);

                INSERT INTO chunks_fts(rowid, content)
                VALUES (new.id, new.content);
            END;
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_messages_conversation
            ON messages(conversation_id)
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_chunks_document
            ON document_chunks(document_id)
        """)

    print("Jawad AI database initialized!")


# ==========================================
# CONVERSATION FUNCTIONS
# ==========================================

def create_conversation(title="New Conversation"):
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO conversations (title) VALUES (?)",
            (title,)
        )
        return cursor.lastrowid


def get_conversations():
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT *
            FROM conversations
            ORDER BY id DESC
        """).fetchall()

        return rows_to_dicts(rows)


def update_conversation_title(conversation_id, title):
    with get_connection() as conn:
        conn.execute("""
            UPDATE conversations
            SET title = ?
            WHERE id = ?
        """, (title, conversation_id))


def delete_conversation(conversation_id):
    with get_connection() as conn:
        conn.execute("""
            DELETE FROM conversations
            WHERE id = ?
        """, (conversation_id,))


# ==========================================
# MESSAGE FUNCTIONS
# ==========================================

def save_message(conversation_id, role, content):
    with get_connection() as conn:
        cursor = conn.execute("""
            INSERT INTO messages
                (conversation_id, role, content)
            VALUES (?, ?, ?)
        """, (conversation_id, role, content))

        return cursor.lastrowid


def get_messages(conversation_id):
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT *
            FROM messages
            WHERE conversation_id = ?
            ORDER BY id ASC
        """, (conversation_id,)).fetchall()

        return rows_to_dicts(rows)


def delete_last_message(conversation_id, role):
    with get_connection() as conn:
        conn.execute("""
            DELETE FROM messages
            WHERE id = (
                SELECT id
                FROM messages
                WHERE conversation_id = ?
                  AND role = ?
                ORDER BY id DESC
                LIMIT 1
            )
        """, (conversation_id, role))


# ==========================================
# AUTOMATIC MEMORY FUNCTIONS
# ==========================================

def save_memory(memory, category="general", importance=3):
    memory = memory.strip()

    if not memory:
        return None

    importance = max(1, min(5, int(importance)))

    with get_connection() as conn:

        existing = conn.execute("""
            SELECT id
            FROM memories
            WHERE LOWER(memory) = LOWER(?)
        """, (memory,)).fetchone()

        if existing:
            conn.execute("""
                UPDATE memories
                SET category = ?,
                    importance = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (category, importance, existing["id"]))

            return existing["id"]

        cursor = conn.execute("""
            INSERT INTO memories
                (category, memory, importance)
            VALUES (?, ?, ?)
        """, (category, memory, importance))

        return cursor.lastrowid


def get_memories(limit=100):
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT *
            FROM memories
            ORDER BY importance DESC, updated_at DESC
            LIMIT ?
        """, (limit,)).fetchall()

        return rows_to_dicts(rows)


def search_memories(query, limit=10):
    words = [
        word.strip()
        for word in query.split()
        if len(word.strip()) > 2
    ]

    if not words:
        return []

    conditions = " OR ".join(
        ["memory LIKE ?" for _ in words]
    )

    parameters = [f"%{word}%" for word in words]
    parameters.append(limit)

    with get_connection() as conn:
        rows = conn.execute(f"""
            SELECT *
            FROM memories
            WHERE {conditions}
            ORDER BY importance DESC, updated_at DESC
            LIMIT ?
        """, parameters).fetchall()

        return rows_to_dicts(rows)


def delete_memory(memory_id):
    with get_connection() as conn:
        conn.execute("""
            DELETE FROM memories
            WHERE id = ?
        """, (memory_id,))


# ==========================================
# DOCUMENT FUNCTIONS
# ==========================================

def save_document(filename, file_type, file_hash):
    with get_connection() as conn:
        cursor = conn.execute("""
            INSERT OR IGNORE INTO documents
                (filename, file_type, file_hash)
            VALUES (?, ?, ?)
        """, (filename, file_type, file_hash))

        return cursor.lastrowid


def save_document_chunk(document_id, chunk_index, content):
    with get_connection() as conn:
        cursor = conn.execute("""
            INSERT INTO document_chunks
                (document_id, chunk_index, content)
            VALUES (?, ?, ?)
        """, (document_id, chunk_index, content))

        return cursor.lastrowid


# ==========================================
# STARTUP
# ==========================================

if __name__ == "__main__":
    init_db()