# agents/memory.py

from langchain.memory import ConversationSummaryBufferMemory

def get_memory(llm):
    return ConversationSummaryBufferMemory(
        return_messages=True,
        memory_key="chat_history",
        llm = llm
    )