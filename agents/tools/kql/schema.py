# agents/tools/kql/schema.py

from pydantic.v1 import BaseModel, Field
from typing import Optional

class KQLQueryInput(BaseModel):
    query: str = Field(..., description="Natural language query or raw KQL to run against the workspace.")
    workspace_id: Optional[str] = Field(
        None,
        description="Azure Log Analytics Workspace ID. If not provided, default from environment will be used."
    )
    time_range: Optional[str] = Field(
        None,
        description="Optional time range like 'last 24 hours', 'yesterday', 'last 7 days', etc."
    )
    summarize: Optional[bool] = Field(
        default=True,
        description="Whether to summarize the results or return raw output."
    )
