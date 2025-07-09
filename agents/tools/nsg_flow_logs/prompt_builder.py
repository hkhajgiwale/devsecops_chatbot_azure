import json
from typing import List

class NSGFlowLogsPromptBuilder:
    def __init__(self, flows: List[dict], query: str = None):
        self.flows = flows
        self.query = query or "N/A"

    def build_prompt(self) -> str:
        preview_flows = self.flows[:100]

        return f"""
You are a DevSecOps AI assistant helping to analyze Azure NSG (Network Security Group) Flow Logs.

User's question: "{self.query}"

Here is a preview of the parsed flow records (limited to 100 for initial context):
{json.dumps(preview_flows, indent=2)}

You can help with:
- 📊 Generating summaries for traffic.
- 🔎 Finding source/destination IPs or ports.
- 🛡️ Spotting denied traffic.
- ⚙️ Improving NSG rules.
- ✍️ Returning clean natural language results (not markdown unless explicitly asked).
- 🕒 If no time range is provided, assume the last 7 days.


Be concise, clear, and user-friendly in your answers. 
If you are asked questions, like how many flows were denied/allowed - in a way it can be quantified, provide a direct answer based on the provided flow records - try to give output in tabular form and ask if they need in any more format or what
"""
