import streamlit as st
import requests


def init_session():
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "history_summary" not in st.session_state:
        st.session_state.history_summary = ""
    if "show_sources" not in st.session_state:
        st.session_state.show_sources = False


def display_chat():
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if st.session_state.show_sources and msg["role"] == "assistant":
                sources = msg.get("sources", [])
                if sources:
                    st.caption(
                        "Sources:\n"
                        + "\n".join(
                            [
                                f"- {s.get('title', '')} (Updated: {s.get('updated_at', s.get('updated', ''))})"
                                for s in sources
                            ]
                        )
                    )


def handle_chat():
    if user_input := st.chat_input("Enter your message..."):
        st.session_state.chat_history.append(
            {"role": "user", "content": user_input}
        )

        try:
            response = requests.post(
                "http://localhost:8000/ask",
                json={
                    "question": user_input,
                    "session_id": None,
                    "history_summary": st.session_state.history_summary,
                    "last_role": [],
                },
                timeout=30,
            )
            if response.status_code == 200:
                data = response.json()
                st.session_state.chat_history.append(
                    {
                        "role": "assistant",
                        "content": data["answer"],
                        "sources": data.get("sources", []),
                    }
                )
            else:
                st.session_state.chat_history.append(
                    {
                        "role": "assistant",
                        "content": f"[Error {response.status_code}] {response.text}",
                        "sources": [],
                    }
                )
        except Exception as e:
            st.session_state.chat_history.append(
                {
                    "role": "assistant",
                    "content": f"[Request failed] {e}",
                    "sources": [],
                }
            )


def handle_summary():
    combined = " ".join(
        [msg["content"] for msg in st.session_state.chat_history]
    )
    st.session_state.history_summary = (
        combined[:50] + "..." if combined else "No data"
    )
    st.markdown(f"**Summary:** {st.session_state.history_summary}")


def main():
    st.set_page_config(page_title="QA Chat", page_icon="💬")
    st.title("💬 QA Chat")

    init_session()
    mode = st.radio("Select mode", ["Chat", "Summarize"])

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Reset"):
            st.session_state.chat_history = []
            st.session_state.history_summary = ""
    with col2:
        st.session_state.show_sources = st.toggle(
            "Show Sources", value=st.session_state.show_sources
        )

    if mode == "Chat":
        handle_chat()
        display_chat()
    elif mode == "Summarize":
        handle_summary()


if __name__ == "__main__":
    main()
