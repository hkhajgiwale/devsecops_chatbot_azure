import json

class NSGFlowLogsPromptBuilder:
    def __init__(self, flows: list[dict]):
        self.flows = flows

    def build_prompt(self) -> str:
        return f"""
You are a DevSecOps AI assistant helping to analyze Azure NSG (Network Security Group) Flow Logs.

Here is a preview of the parsed flow records (limited to 100 for initial context):
{json.dumps(self.flows[:100], indent=2)}

You can help with:
- 📊 Generating summary tables for traffic patterns.
- 🔎 Identifying frequent source/destination IPs or ports.
- 🛡️ Highlighting potentially risky or unusual flows.
- ⚙️ Recommending NSG rule improvements based on flow behavior.
- 📁 Structuring data into markdown tables for documentation or reporting.

Please wait for the user to ask specific questions or request analyses. Be concise, accurate, and ready to drill down on request.
"""
