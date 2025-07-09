# agents/agent_router.py

from openai import AzureOpenAI
from agents.tools._core.tool_registry import ToolRegistry
import os

class RouterAgent:
    def __init__(self, registry: ToolRegistry, client: AzureOpenAI):
        self.registry = registry
        self.client = client

    def route(self, query: str) -> tuple[str, str]:
        if not query.strip():
            return "", ""

        tools_list = self.registry.list_tools()
        tool_names = "\n".join(f"- {name}" for name in tools_list)

        system_prompt = (
            "You are a DevSecOps tool router. Based on the user's question:\n"
            f"{query}\n\n"
            "Pick the best matching tool strictly from this list:\n"
            f"{tool_names}\n\n"
            "If the tool is 'Azure Sentinel KQL Query', also generate the appropriate KQL query.\n"
            "Respond in this format (no explanation):\n"
            "{tool_name}|||{optional_kql_or_blank}"
        )

        try:
            response = self.client.chat.completions.create(
                model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ]
            )

            content = response.choices[0].message.content.strip()
            if "|||" in content:
                tool_name, kql = content.split("|||", 1)
                return tool_name.strip(), kql.strip()
            return content.strip(), ""

        except Exception as e:
            print(f"⚠️ Router failed: {e}")
            return "", ""
