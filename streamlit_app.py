
import streamlit as st
from openai import OpenAI

from memory.database import (
    init_db,
    create_conversation,
    get_conversations,
    delete_conversation,
    save_message,
    get_messages,
    delete_last_message
)

# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Jawads AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# DATABASE INITIALIZATION
# ==========================================

init_db()

# ==========================================
# API CONFIGURATION
# ==========================================

try:
    API_KEY = st.secrets["OPENROUTER_API_KEY"]
except Exception:
    st.error("OpenRouter API key not found. Configure it in Streamlit Secrets.")
    st.stop()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY,
    default_headers={
        "HTTP-Referer": "https://jawad-open.streamlit.app",
        "X-Title": "Jawad AI"
    }
)

MODEL = "openrouter/free"

SYSTEM_PROMPT = """
You are Jawad AI, a helpful, intelligent and professional AI assistant.

Give clear, accurate, friendly and well-structured answers.

When explaining technical topics, use beginner-friendly,
step-by-step instructions.

Be honest when you are uncertain.
"""

# ==========================================
# SESSION STATE
# ==========================================

if "theme" not in st.session_state:
    st.session_state.theme = "Dark"

if "conversation_id" not in st.session_state:

    conversations = get_conversations()

    if conversations:
        st.session_state.conversation_id = conversations[0]["id"]
    else:
        st.session_state.conversation_id = create_conversation()

if "messages" not in st.session_state:
    st.session_state.messages = get_messages(
        st.session_state.conversation_id
    )

# ==========================================
# CONVERSATION SWITCHING
# ==========================================

def switch_conversation(conversation_id):

    st.session_state.conversation_id = conversation_id

    st.session_state.messages = get_messages(
        conversation_id
    )

    st.rerun()


# ==========================================
# THEME COLORS
# ==========================================

dark_mode = st.session_state.theme == "Dark"

if dark_mode:
    BG = "#0e1117"
    SIDEBAR = "#161b25"
    CARD = "#1b2230"
    TEXT = "#f5f7fb"
    MUTED = "#a5afc0"
    BORDER = "#30394a"
    INPUT_BG = "#252d3b"

else:
    BG = "#f7f9fc"
    SIDEBAR = "#ffffff"
    CARD = "#ffffff"
    TEXT = "#172033"
    MUTED = "#667085"
    BORDER = "#e2e8f0"
    INPUT_BG = "#ffffff"

# ==========================================
# CUSTOM CSS
# ==========================================

st.markdown(
    f"""
    <style>

    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
    }}

    .stApp {{
        background-color: {BG};
        color: {TEXT};
    }}

    [data-testid="stHeader"] {{
        background-color: {BG};
    }}

    [data-testid="stSidebar"] {{
        background-color: {SIDEBAR};
        border-right: 1px solid {BORDER};
    }}

    [data-testid="stSidebar"] * {{
        color: {TEXT};
    }}

    .brand {{
        font-size: 27px;
        font-weight: 800;
        color: #3978ed;
        letter-spacing: -1px;
        margin-bottom: 2px;
    }}

    .brand-subtitle {{
        font-size: 12px;
        color: {MUTED};
        margin-bottom: 25px;
    }}

    .main-heading {{
        font-size: 36px;
        font-weight: 800;
        letter-spacing: -1.5px;
        color: {TEXT};
        text-align: center;
        margin-top: 35px;
        margin-bottom: 8px;
    }}

    .main-subtitle {{
        color: {MUTED};
        font-size: 15px;
        text-align: center;
        margin-bottom: 35px;
    }}

    .welcome-card {{
        background: {CARD};
        border: 1px solid {BORDER};
        border-radius: 18px;
        padding: 25px;
        margin: 10px 0;
    }}

    .welcome-card h3 {{
        color: {TEXT};
        font-size: 17px;
        margin-bottom: 8px;
    }}

    .welcome-card p {{
        color: {MUTED};
        font-size: 13px;
        margin-bottom: 0;
    }}

    .status {{
        display: inline-block;
        background: rgba(34,197,94,0.12);
        color: #22c55e;
        border-radius: 20px;
        padding: 6px 12px;
        font-size: 12px;
        font-weight: 600;
    }}

    .footer {{
        text-align: center;
        color: {MUTED};
        font-size: 11px;
        padding: 25px 0 10px 0;
    }}

    [data-testid="stChatInput"] {{
        background-color: {BG} !important;
    }}

    [data-testid="stChatInput"] > div {{
        background-color: {INPUT_BG} !important;
        border: 1px solid {BORDER} !important;
        border-radius: 15px !important;
    }}

    [data-testid="stChatInput"] textarea {{
        color: {TEXT} !important;
        -webkit-text-fill-color: {TEXT} !important;
        caret-color: {TEXT} !important;
        background-color: transparent !important;
    }}

    [data-testid="stChatInput"] textarea::placeholder {{
        color: {MUTED} !important;
        opacity: 1 !important;
    }}

    [data-testid="stChatMessage"] {{
        background-color: {CARD};
        border: 1px solid {BORDER};
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 12px;
    }}

    [data-testid="stMarkdownContainer"] p {{
        color: {TEXT};
    }}

    .stButton > button {{
        border-radius: 10px;
        border: 1px solid {BORDER};
        background-color: {CARD};
        color: {TEXT};
        font-weight: 600;
        transition: 0.2s ease;
    }}

    .stButton > button:hover {{
        border-color: #3978ed;
        color: #3978ed;
    }}

    </style>
    """,
    unsafe_allow_html=True
)

# ==========================================
# SIDEBAR
# ==========================================

with st.sidebar:

    st.markdown(
        """
        <div class="brand">✦ Jawad AI</div>
        <div class="brand-subtitle">Your personal AI assistant</div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

    # NEW CONVERSATION

    if st.button("＋ New Conversation", use_container_width=True):

        new_id = create_conversation()

        st.session_state.conversation_id = new_id
        st.session_state.messages = []

        st.rerun()

    # APPEARANCE

    st.markdown("### Appearance")

    theme_choice = st.radio(
        "Choose theme",
        ["Dark", "Light"],
        index=0 if dark_mode else 1,
        horizontal=True,
        label_visibility="collapsed"
    )

    if theme_choice != st.session_state.theme:
        st.session_state.theme = theme_choice
        st.rerun()

    st.markdown("---")

    # AI MODEL

    st.markdown("### AI Model")

    st.selectbox(
        "Selected model",
        [MODEL],
        index=0,
        disabled=True,
        label_visibility="collapsed"
    )

    st.caption("Powered by OpenRouter")

    st.markdown("---")

    # CONVERSATION HISTORY

    st.markdown("### Conversation History")

    conversations = get_conversations()

    if conversations:

        for conversation in conversations:

            conversation_id = conversation["id"]

            title = conversation["title"] or "New Conversation"

            if len(title) > 24:
                title = title[:24] + "..."

            if conversation_id == st.session_state.conversation_id:
                title = "● " + title

            if st.button(
                title,
                key=f"conversation_{conversation_id}",
                use_container_width=True
            ):
                switch_conversation(conversation_id)

    st.caption(
        f"{len(st.session_state.messages) // 2} messages in current conversation"
    )

    # CLEAR CONVERSATION

    st.markdown("---")

    if st.button("🗑️ Clear Conversation", use_container_width=True):

        delete_conversation(
            st.session_state.conversation_id
        )

        new_id = create_conversation()

        st.session_state.conversation_id = new_id
        st.session_state.messages = []

        st.rerun()

    st.markdown("---")

    st.markdown(
        """
        <div style="font-size:12px; color:#8993a5;">
            <b>Jawad AI</b><br>
            Built with Python and Streamlit.<br>
            Powered by OpenRouter.
        </div>
        """,
        unsafe_allow_html=True
    )

# ==========================================
# MAIN HEADER
# ==========================================

st.markdown(
    """
    <div style="text-align:center; margin-top:10px;">
        <span class="status">● Online</span>
    </div>
    """,
    unsafe_allow_html=True
)

# ==========================================
# WELCOME SCREEN
# ==========================================

suggested_prompt = None

if not st.session_state.messages:

    st.markdown(
        """
        <div class="main-heading">
            How can I help you today?
        </div>

        <div class="main-subtitle">
            Ask anything. Explore ideas, solve problems,
            and build something great.
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            """
            <div class="welcome-card">
                <h3>💻 Programming</h3>
                <p>Learn Python, debug code, and develop applications.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button(
            "Teach me Python from beginner to advanced",
            use_container_width=True
        ):
            suggested_prompt = "Teach me Python from beginner to advanced."

    with col2:

        st.markdown(
            """
            <div class="welcome-card">
                <h3>🤖 Artificial Intelligence</h3>
                <p>Explore AI concepts, tools, models, and projects.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button(
            "Explain how AI agents work",
            use_container_width=True
        ):
            suggested_prompt = "Explain how AI agents work."

    col3, col4 = st.columns(2)

    with col3:

        st.markdown(
            """
            <div class="welcome-card">
                <h3>🔐 Cyber Security</h3>
                <p>Understand security concepts and best practices.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button(
            "Give me a cyber security learning roadmap",
            use_container_width=True
        ):
            suggested_prompt = "Give me a cyber security learning roadmap."

    with col4:

        st.markdown(
            """
            <div class="welcome-card">
                <h3>💡 Ideas & Creativity</h3>
                <p>Brainstorm ideas and turn your plans into reality.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button(
            "Give me an innovative project idea",
            use_container_width=True
        ):
            suggested_prompt = "Give me an innovative project idea."

else:

    st.markdown(
        """
        <div style="text-align:center; padding:15px 0;">
            <span style="font-size:25px; font-weight:800; color:#3978ed;">
                ✦ Jawad AI
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )

# ==========================================
# DISPLAY CHAT HISTORY
# ==========================================

for message in st.session_state.messages:

    if message["role"] == "user":

        with st.chat_message("user", avatar="👤"):
            st.markdown(message["content"])

    else:

        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(message["content"])

# ==========================================
# CHAT INPUT
# ==========================================

user_input = st.chat_input(
    "Message Jawads AI...",
    key="jawad_chat_input"
)

if suggested_prompt:
    user_input = suggested_prompt

# ==========================================
# GENERATE AI RESPONSE
# ==========================================

if user_input:

    # SAVE USER MESSAGE

    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    save_message(
        st.session_state.conversation_id,
        "user",
        user_input
    )

    # SET CONVERSATION TITLE

    if len(st.session_state.messages) == 1:

        from memory.database import update_conversation_title

        update_conversation_title(
            st.session_state.conversation_id,
            user_input[:50]
        )

    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)

    with st.chat_message("assistant", avatar="🤖"):

        response_placeholder = st.empty()

        with st.spinner("Jawad AI is thinking..."):

            try:

                response = client.chat.completions.create(
                    model=MODEL,
                    messages=[
                        {
                            "role": "system",
                            "content": SYSTEM_PROMPT
                        }
                    ] + st.session_state.messages,
                    temperature=0.7,
                    max_tokens=2000
                )

                assistant_reply = (
                    response.choices[0].message.content
                )

                if not assistant_reply:
                    assistant_reply = (
                        "I couldn't generate a response. Please try again."
                    )

                response_placeholder.markdown(
                    assistant_reply
                )

                # SAVE ASSISTANT RESPONSE

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": assistant_reply
                })

                save_message(
                    st.session_state.conversation_id,
                    "assistant",
                    assistant_reply
                )

            except Exception as e:

                error_message = (
                    "Sorry, something went wrong while connecting "
                    "to the AI service. Please try again."
                )

                response_placeholder.error(error_message)

                # ROLLBACK FAILED USER MESSAGE

                if (
                    st.session_state.messages
                    and st.session_state.messages[-1]["role"] == "user"
                ):
                    st.session_state.messages.pop()

                delete_last_message(
                    st.session_state.conversation_id,
                    "user"
                )

                st.caption(f"Technical details: {str(e)}")

# ==========================================
# FOOTER
# ==========================================

st.markdown(
    """
    <div class="footer">
        Jawad AI - Built with Python, Streamlit & OpenRouter
    </div>
    """,
    unsafe_allow_html=True
)
