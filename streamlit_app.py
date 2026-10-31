
import streamlit as st
from openai import OpenAI

# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Jawad's AI assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# SESSION STATE
# ==========================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "theme" not in st.session_state:
    st.session_state.theme = "Light"

if "model" not in st.session_state:
    st.session_state.model = "openrouter/free"

# ==========================================
# OPENROUTER CONNECTION
# ==========================================

try:
    API_KEY = st.secrets["OPENROUTER_API_KEY"]

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=API_KEY
    )

except Exception:
    st.error("OpenRouter configuration is missing.")
    st.stop()

# ==========================================
# CUSTOM STYLING
# ==========================================

dark = st.session_state.theme == "Dark"

if dark:
    bg = "#111318"
    sidebar = "#191c24"
    surface = "#202530"
    text = "#f1f5f9"
    muted = "#a0a9b8"
    border = "#303746"
else:
    bg = "#f7f9fc"
    sidebar = "#ffffff"
    surface = "#ffffff"
    text = "#172033"
    muted = "#697586"
    border = "#e5eaf1"

st.markdown(f"""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
}}

.stApp {{
    background: {bg};
    color: {text};
}}

[data-testid="stSidebar"] {{
    background: {sidebar};
    border-right: 1px solid {border};
}}

[data-testid="stHeader"] {{
    background: transparent;
}}

.block-container {{
    max-width: 1050px;
    padding-top: 2rem;
    padding-bottom: 7rem;
}}

.brand {{
    font-size: 27px;
    font-weight: 800;
    letter-spacing: -1px;
    color: {text};
}}

.brand span {{
    color: #3978f6;
}}

.brand-sub {{
    font-size: 12px;
    color: {muted};
    margin-top: 4px;
}}

.section-label {{
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1.3px;
    color: {muted};
    margin: 22px 0 10px 0;
}}

.welcome {{
    text-align: center;
    padding: 75px 15px 35px 15px;
}}

.welcome-icon {{
    font-size: 45px;
    margin-bottom: 15px;
}}

.welcome h1 {{
    color: {text};
    font-size: 38px;
    font-weight: 800;
    letter-spacing: -1.5px;
}}

.welcome p {{
    color: {muted};
    font-size: 15px;
}}

.info-card {{
    background: {surface};
    border: 1px solid {border};
    border-radius: 16px;
    padding: 17px;
    min-height: 105px;
}}

.info-card b {{
    color: {text};
    font-size: 14px;
}}

.info-card p {{
    color: {muted};
    font-size: 12px;
    margin-top: 8px;
}}

[data-testid="stChatMessage"] {{
    background: {surface};
    border: 1px solid {border};
    border-radius: 15px;
    padding: 15px;
    margin-bottom: 15px;
}}

[data-testid="stChatInput"] {{
    border-radius: 16px;
}}

.stButton > button {{
    border-radius: 11px;
    border: 1px solid {border};
    background: {surface};
    color: {text};
    font-weight: 500;
    transition: 0.2s;
}}

.stButton > button:hover {{
    border-color: #3978f6;
    color: #3978f6;
}}

hr {{
    border-color: {border};
}}

.footer {{
    text-align: center;
    font-size: 11px;
    color: {muted};
    padding: 15px;
}}

</style>
""", unsafe_allow_html=True)

# ==========================================
# SIDEBAR
# ==========================================

with st.sidebar:

    st.markdown(
        '<div class="brand">Jawad<span>AI.</span></div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="brand-sub">Your intelligent AI companion</div>',
        unsafe_allow_html=True
    )

    st.write("")

    if st.button("＋  New Conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown('<div class="section-label">AI MODEL</div>',
                unsafe_allow_html=True)

    selected_model = st.selectbox(
        "Select model",
        options=[
            "openrouter/free",
        ],
        format_func=lambda x: "Auto • Free Models"
    )

    st.session_state.model = selected_model

    st.markdown('<div class="section-label">APPEARANCE</div>',
                unsafe_allow_html=True)

    theme = st.radio(
        "Choose theme",
        ["Light", "Dark"],
        index=0 if st.session_state.theme == "Light" else 1,
        horizontal=True,
        label_visibility="collapsed"
    )

    if theme != st.session_state.theme:
        st.session_state.theme = theme
        st.rerun()

    st.markdown('<div class="section-label">CONVERSATION</div>',
                unsafe_allow_html=True)

    st.caption(f"{len(st.session_state.messages) // 2} exchanges")

    if st.button("Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.divider()

    st.markdown(
        f"""
        <div style="font-size:13px;color:{muted};">
        <b style="color:{text};">Jawad's AI assistant</b><br>
        Powered by OpenRouter<br><br>
        Personal AI Assistant
        </div>
        """,
        unsafe_allow_html=True
    )

# ==========================================
# MAIN HEADER
# ==========================================

col1, col2 = st.columns([3, 1])

with col1:
    st.markdown(
        f"<h3 style='color:{text};margin-bottom:0;'>AI Assistant</h3>",
        unsafe_allow_html=True
    )
    st.caption("Ask questions, explore ideas and get things done.")

with col2:
    st.markdown(
        f"""
        <div style="text-align:right;padding-top:8px;
        color:#16a36a;font-size:12px;">
        ● ONLINE
        </div>
        """,
        unsafe_allow_html=True
    )

st.divider()

# ==========================================
# WELCOME SCREEN
# ==========================================

if not st.session_state.messages:

    st.markdown("""
    <div class="welcome">
        <div class="welcome-icon">✦</div>
        <h1>What can I help you with?</h1>
        <p>Your ideas deserve intelligent answers. Let's get started.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-label">TRY ASKING</div>',
                unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    prompt = None

    with col1:
        if st.button(
            "💡  Explain a concept\n\nLearn something new",
            use_container_width=True
        ):
            prompt = "Explain artificial intelligence in simple words."

        if st.button(
            "💻  Write Python code\n\nBuild something useful",
            use_container_width=True
        ):
            prompt = "Write a Python program to demonstrate an API."

    with col2:
        if st.button(
            "✍️  Improve my writing\n\nMake it professional",
            use_container_width=True
        ):
            prompt = "Help me write a professional email."

        if st.button(
            "🚀  Brainstorm ideas\n\nExplore new possibilities",
            use_container_width=True
        ):
            prompt = "Give me five creative technology project ideas."

else:
    prompt = None

# ==========================================
# DISPLAY CHAT HISTORY
# ==========================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"],
        avatar="👤" if message["role"] == "user" else "✦"
    ):
        st.markdown(message["content"])

# ==========================================
# CHAT INPUT
# ==========================================

user_input = st.chat_input("Message Jawad AI...")

if user_input:
    prompt = user_input

# ==========================================
# GENERATE RESPONSE
# ==========================================

if prompt:

    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="✦"):

        try:
            with st.spinner("Thinking..."):

                response = client.chat.completions.create(
                    model=st.session_state.model,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are Jasper AI created by M. Jawad, a professional, "
                                "friendly and intelligent assistant. "
                                "Provide accurate, clear and helpful answers. "
                                "Use Markdown and code formatting when useful."
                            )
                        },
                        *st.session_state.messages
                    ],
                    temperature=0.7
                )

                answer = response.choices[0].message.content

                if not answer:
                    answer = "I couldn't generate a response. Please try again."

                st.markdown(answer)

                st.caption(f"Model: {response.model}")

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })

        except Exception as e:
            st.error(f"Something went wrong: {str(e)}")

st.markdown(
    '<div class="footer">Jawad's AI · Built with Python, Streamlit & OpenRouter</div>',
    unsafe_allow_html=True
)
