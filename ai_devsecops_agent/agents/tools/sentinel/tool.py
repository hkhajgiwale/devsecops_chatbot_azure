from datetime import datetime, timedelta
from azure.identity import DefaultAzureCredential
from azure.monitor.query import LogsQueryClient
from agents.tools._core.base_tool import BaseTool
import os

class SentinelTool(BaseTool):
    def __init__(self):
        self.workspace_id = os.getenv("AZURE_LOG_ANALYTICS_WORKSPACE_ID")
        self.client = LogsQueryClient(credential=DefaultAzureCredential())

    def name(self) -> str:
        return "Azure Sentinel"

    @classmethod
    def register_tool(cls):
        return cls()

    def _ensure_tabular(self, kql: str) -> str:
        """
        Wrap scalar expressions into a tabular result if needed.
        """
        kql = kql.strip()
        scalar_keywords = ["count", "distinct", "toscalar", "summarize"]
        is_scalar = (
            not any(keyword in kql.lower() for keyword in ["project", "extend", "summarize", "| top", "order by"])
            and any(kw in kql.lower() for kw in scalar_keywords)
        )

        if is_scalar:
            return f"datatable(dummy:int)[1] | extend result=({kql}) | project result"

        return kql

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
