from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import AzureChatOpenAI
from agents.memory import get_memory
from agents.tool_factory import load_tools
import os
from dotenv import load_dotenv

load_dotenv()
def get_router_agent():
    llm = AzureChatOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        openai_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    )

    tools = load_tools()
    for t in tools:
        print(f"✅ Loaded tool: {t.name}")

    memory = get_memory(llm=llm)

    # ✅ Define the system prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful DevSecOps assistant. Use the tools provided to answer user queries."),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    # ✅ Create the agent
    agent = create_openai_functions_agent(llm=llm, tools=tools, prompt=prompt)

    # ✅ Wrap in executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True,
        max_iterations=30,
        max_execution_time=180,
        handle_parsing_errors=True,
    )

    return agent_executor
