# app.py
import streamlit as st
from rag_pipeline import load_combined_qa_chain
from datetime import datetime

st.set_page_config(page_title="AskF1", page_icon="🏎️")

# Setup app title
st.title("🏎️ AskF1 – Your F1 Knowledge Assistant")

if 'messages' not in st.session_state:
    st.session_state.messages = []

# Displays chat history
for message in st.session_state.messages:
    st.chat_message(message['role']).markdown(message['content'])


def enrich_prompt(user_question: str):
    today = datetime.today().strftime("%B %d, %Y")
    return f"(Today is {today}) {user_question}"

# Prompt input template to display prompts
prompt = st.chat_input('Ask your F1 question')
qa_chain = load_combined_qa_chain()


if prompt:
    # Display prompt
    st.chat_message('user').markdown(prompt)

    # Add user prompt in state
    st.session_state.messages.append({'role': 'user', 'content': prompt})
    with st.spinner("Thinking..."):
        result = qa_chain.invoke(enrich_prompt(prompt))
        answer = result['result']
        sources = result['source_documents']
    
    # Show agent's response
    st.chat_message('assistant').markdown(answer)

    # ✅ Display sources
    with st.expander("📚 Sources"):
        for i, source in enumerate(sources):
            metadata = source.metadata
            snippet = source.page_content[:300].strip().replace("\n", " ")
            st.markdown(f"**{i+1}. Source**: `{metadata.get('source', 'Unknown')}`")
            st.markdown(f"> {snippet}...")

    # Add agent's response to chat history
    st.session_state.messages.append({'role': 'assistant', 'content': answer})
 