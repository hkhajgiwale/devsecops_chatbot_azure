# agents/tools/kql/tool.py

import os
from dotenv import load_dotenv
from typing import Optional
from datetime import datetime, timedelta

from azure.identity import DefaultAzureCredential
from azure.monitor.query import LogsQueryClient, LogsQueryStatus
from langchain_core.tools import StructuredTool, Tool
from langchain_openai import AzureChatOpenAI

from agents.utils.time_parser import parse_time_range
from agents.tools.kql.schema import KQLQueryInput
from agents.tools.kql.prompt_builder import KQLPromptBuilder

load_dotenv()

DEFAULT_WORKSPACE_ID = os.getenv("AZURE_LOG_ANALYTICS_WORKSPACE_ID")
DEFAULT_LOOKBACK_DAYS = int(os.getenv("DEFAULT_LOOKBACK_DAYS", 7))

llm = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    openai_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
)

def run_kql_query(input: KQLQueryInput) -> str:
    try:
        workspace_id = input.workspace_id or DEFAULT_WORKSPACE_ID
        if not workspace_id:
            return "❌ Workspace ID is missing. Please provide one or set AZURE_LOG_ANALYTICS_WORKSPACE_ID in .env."

        # Parse time range
        if input.time_range:
            start_time, end_time = parse_time_range(input.time_range)
        else:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=DEFAULT_LOOKBACK_DAYS)

        # Translate NL to KQL if needed
        if not input.query.strip().lower().startswith("azurediagnostics") and " | " not in input.query:
            prompt = KQLPromptBuilder.build_prompt(input.query, input.time_range)
            input.query = llm.invoke(prompt).content.strip()

        print(f"📥 Final KQL:\n{input.query}")

        # Run query
        client = LogsQueryClient(credential=DefaultAzureCredential())
        response = client.query_workspace(
            workspace_id=workspace_id,
            query=input.query,
            timespan=(start_time, end_time)
        )

        if response.status != LogsQueryStatus.SUCCESS:
            return f"⚠️ Query failed: {response.status}"

        table = response.tables[0]
        rows = table.rows
        columns = [col.name for col in table.columns]

        if not rows:
            return "✅ Query succeeded but returned no results."

        if input.summarize:
            return f"✅ Found {len(rows)} rows.\n\nColumns: {', '.join(columns)}\n\nSample:\n{rows[0]}"
        else:
            return f"✅ Raw Results:\nColumns: {', '.join(columns)}\n\n" + "\n".join(str(row) for row in rows[:5])

    except Exception as e:
        return f"❌ Error running KQL query: {str(e)}"

def fallback_response(query: str) -> str:
    return f"I'm sorry, I couldn't understand your query: '{query}'. Please rephrase or check for typos."

fallback_tool = Tool(
    name="KQLFallbackResponder",
    func=fallback_response,
    description="Handles queries that do not match any known KQL pattern."
)

def get_tools():
    return [
        StructuredTool.from_function(
            name="KQLQueryTool",
            func=lambda **kwargs: run_kql_query(KQLQueryInput(**kwargs)),
            description="Run KQL queries against Azure Log Analytics. Accepts natural language or raw KQL.",
            args_schema=KQLQueryInput
        ),
        fallback_tool
    ]
