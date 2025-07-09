from datetime import datetime, timedelta
from azure.identity import DefaultAzureCredential
from azure.monitor.query import LogsQueryClient
from agents.tools._core.base_tool import BaseTool
import os

class KQLTool(BaseTool):
    def name(self) -> str:
        return "Azure KQL Query"

    @classmethod
    def register_tool(cls):
        return cls()

    def run(self, **kwargs) -> str:
        kql = kwargs.get("kql")
        if not kql:
            return "❌ No KQL query provided."

        kql = self._ensure_tabular(kql)

        print(f"🧾 Executing KQL:\n{kql}\n")

        try:
            response = self.client.query_workspace(
                workspace_id=self.workspace_id,
                query=kql,
                timespan=(datetime.utcnow() - timedelta(hours=5), datetime.utcnow())
            )
        except Exception as e:
            return f"❌ Query failed: {str(e)}"

        if not response.tables:
            return "⚠️ No results found."

        table = response.tables[0]
        columns = [col.name for col in table.columns]
        rows = [[str(cell) for cell in row] for row in table.rows]

        output = [", ".join(columns)]
        output += [", ".join(row) for row in rows[:10]]  # Limit to 10 rows
        return "\n".join(output)
