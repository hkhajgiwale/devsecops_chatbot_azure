import os
import uuid
from dotenv import load_dotenv
from openai import AzureOpenAI

from agents.memory.thread import Thread
from agents.tools._core.tool_registry import ToolRegistry
from agents.tools._core.tool_loader import load_tools
from agents.agent_router import RouterAgent

load_dotenv()

class AgentManager:
    def __init__(self):
        self.thread = Thread(id=str(uuid.uuid4()), messages=[])
        self.registry = ToolRegistry()
        self.client = AzureOpenAI(
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        )
        self._load_all_tools()
        self.router = RouterAgent(self.registry, self.client)

    def _load_all_tools(self):
        tools = load_tools()
        for tool in tools:
            self.registry.register(tool)

    def route_and_run(self, query: str):
        tool_name, kql_query = self.router.route(query)

        if not tool_name:
            print("❌ No suitable tool found or empty query. Please rephrase your question.")
            return

        tool = self.registry.get_tool(tool_name)
        if not tool:
            print(f"❌ Tool '{tool_name}' not found in registry.")
            return

        self.thread.add_user_message(query)

        # If KQL is provided (e.g., for Sentinel), pass it
        if kql_query:
            print(f"\n🧾 Executing KQL:\n{kql_query}")
            result = tool.run(kql=kql_query)
        else:
            result = tool.run()

        self.thread.add_agent_message(result)
        print(f"\n🤖 {tool_name}:\n{result}")


    def chat(self):
        print("\n🧠 Multi-tool mode. Ask your question. Type 'exit' to quit.\n")
        while True:
            query = input("🧑‍💻 You: ")
            if query.strip().lower() in {"exit", "quit"}:
                break
            self.route_and_run(query)
