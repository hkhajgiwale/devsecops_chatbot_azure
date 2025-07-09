import os
from dotenv import load_dotenv
from langchain.agents import initialize_agent, AgentType
from langchain_openai import AzureChatOpenAI
from agents.memory import get_memory
from agents.tool_factory import load_tools

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

    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.OPENAI_FUNCTIONS,
        memory=memory,
        verbose=True,
        max_iterations=30,
        max_execution_time=180,
        handle_parsing_errors=True,
    )
    return agent
