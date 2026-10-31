
import streamlit as st
from openai import OpenAI

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="Jawad's AI Chatbot",
    page_icon="🤖",
    layout="centered"
)

# ---------------- API CONFIG ----------------

try:
    API_KEY = st.secrets["OPENROUTER_API_KEY"]
except Exception:
    st.error("OpenRouter API key is missing. Configure your secrets.")
    st.stop()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY
)

# ---------------- SESSION STATE ----------------

if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------- SIDEBAR ----------------

st.sidebar.title("⚙️ Settings")

model_options = {
    "Auto (Free Models Router)": "openrouter/free",
    "Custom Free Model": "custom"
}

selected_option = st.sidebar.selectbox(
    "Choose AI Model",
    list(model_options.keys())
)

if selected_option == "custom":
    model = st.sidebar.text_input(
        "OpenRouter Model ID",
        placeholder="provider/model-name:free"
    )
else:
    model = model_options[selected_option]

st.sidebar.divider()

if st.sidebar.button("🗑️ Clear Chat", use_container_width=True):
    st.session_state.messages = []
    st.rerun()

st.sidebar.caption("Powered by OpenRouter + Streamlit")

# ---------------- MAIN CHAT ----------------

st.title("🤖 Jawad AI Assistant")
st.caption("Your personal AI chatbot created by jawad and powered by free OpenRouter models.")

# Display previous messages

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ---------------- USER INPUT ----------------

if prompt := st.chat_input("Ask me anything..."):

    if not model:
        st.warning("Please enter a model ID.")
        st.stop()

    # Save and display user message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate AI response
    with st.chat_message("assistant"):

        try:
            with st.spinner("Thinking..."):

                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a helpful, friendly AI assistant. created by muhammad jawad "
                                "Give clear and useful answers."
                            )
                        },
                        *st.session_state.messages
                    ],
                    temperature=0.7
                )

                answer = response.choices[0].message.content

                if not answer:
                    answer = "The AI returned an empty response."

                st.markdown(answer)

            # Save assistant response
            st.session_state.messages.append({
                "role": "assistant",
                "content": answer
            })

            st.caption(f"Model used: {response.model}")

        except Exception as e:
            st.error(f"API Error: {str(e)}")
