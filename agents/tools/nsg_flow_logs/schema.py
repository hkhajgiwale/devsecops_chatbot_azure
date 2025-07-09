# agents/tools/nsg_flow_logs/schema.py

from pydantic.v1 import BaseModel, Field  # ✅ Force Pydantic v1
from typing import Optional

class NSGQueryInput(BaseModel):
    query: str = Field(..., description="Natural language query about NSG flow logs.")
    time_range: Optional[str] = Field(
        None, description="Optional time range like 'last 7 days', 'yesterday', etc."
    )
