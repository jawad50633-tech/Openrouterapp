import json
import re

from memory.database import save_memory, search_memories


# ==========================================
# MEMORY EXTRACTION
# ==========================================

MEMORY_SYSTEM_PROMPT = """
You are the memory manager for Jawad AI.

Your task is to identify useful, long-term facts explicitly
shared by the USER.

Save only information that may improve future conversations:
- Professional background and skills
- Long-term projects
- Stable preferences
- Learning goals
- Work and study context
- Communication preferences

Rules:
1. Extract facts only from the user's message.
2. Never treat assistant-generated claims as user facts.
3. Do not save ordinary questions or temporary requests.
4. Do not save passwords, API keys, tokens, or credentials.
5. Do not save sensitive personal information such as health,
   religion, political views, or sexual information.
6. Do not invent or assume facts.
7. Avoid duplicates and keep each memory concise.
8. Return no more than 5 memories.

Return valid JSON in this exact structure:

{
  "memories": [
    {
      "category": "professional",
      "memory": "The user is a Python developer.",
      "importance": 4
    }
  ]
}

If there is nothing worth remembering, return:

{"memories": []}

Allowed categories:
professional, project, preference, learning, general
"""


def extract_memories(client, model, user_message, assistant_reply=""):
    """
    Extract stable facts from a user's message using OpenRouter.
    Only user_message is considered a source of facts.
    """

    if not user_message or len(user_message.strip()) < 15:
        return []

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": MEMORY_SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": (
                        "Analyze this user message and extract "
                        "only explicitly stated long-term facts:\n\n"
                        + user_message[:5000]
                    )
                }
            ],
            temperature=0.1,
            max_tokens=500
        )

        raw = response.choices[0].message.content or ""
        raw = raw.strip()

        # Remove optional Markdown code fences.
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)

        data = json.loads(raw)
        extracted = data.get("memories", [])

        saved = []

        allowed_categories = {
            "professional",
            "project",
            "preference",
            "learning",
            "general"
        }

        for item in extracted[:5]:
            if not isinstance(item, dict):
                continue

            memory = item.get("memory", "")
            category = item.get("category", "general")
            importance = item.get("importance", 3)

            if not isinstance(memory, str):
                continue

            memory = memory.strip()

            if not memory or len(memory) > 500:
                continue

            if category not in allowed_categories:
                category = "general"

            try:
                importance = int(importance)
            except (TypeError, ValueError):
                importance = 3

            importance = max(1, min(5, importance))

            memory_id = save_memory(
                memory=memory,
                category=category,
                importance=importance
            )

            if memory_id:
                saved.append(memory)

        return saved

    except Exception as error:
        print(f"Memory extraction error: {error}")
        return []


# ==========================================
# MEMORY RETRIEVAL
# ==========================================

def get_memory_context(user_message, limit=5):
    """
    Find memories related to the current user message
    and format them for the chatbot.
    """

    memories = search_memories(
        query=user_message,
        limit=limit
    )

    if not memories:
        return ""

    memory_text = "\n".join(
        f"- {item['memory']}"
        for item in memories
    )

    return (
        "Relevant information remembered from previous "
        "conversations:\n"
        f"{memory_text}\n\n"
        "Use these facts only when relevant. "
        "Do not assume information beyond these facts."
    )
