# app.py

import streamlit as st
from agents.router import get_router_agent

# Init agent once and cache
@st.cache_resource
def load_agent():
    return get_router_agent()

agent = load_agent()

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("🔐 DevSecOps Chatbot")

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Accept new user input
if prompt := st.chat_input("Ask me about NSG flow logs..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        # 👇 Use the LangChain agent here!
        response = agent.invoke({"input": prompt})
        output = response["output"]

        st.session_state.messages.append({"role": "assistant", "content": output})
        with st.chat_message("assistant"):
            st.markdown(output)

    except Exception as e:
        err_msg = f"❌ Error: {str(e)}"
        st.session_state.messages.append({"role": "assistant", "content": err_msg})
        with st.chat_message("assistant"):
            st.error(err_msg)
