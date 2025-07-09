# agents/tools/kql/prompt_builder.py

from typing import Optional

class KQLPromptBuilder:
    @staticmethod
    def build_prompt(nl_query: str, time_range: Optional[str] = None) -> str:
        return f"""
You are a DevSecOps assistant skilled in Azure Monitor and Kusto Query Language (KQL).

Your task is to translate the following natural language query into a valid KQL query that can be executed against a Log Analytics workspace.

User's question: "{nl_query}"

Time range: "{time_range or 'last 7 days'}"

---

📌 Examples of natural language to KQL mappings:

1. **"What are the latest firewall logs on XXX?"**
```kql
AzureDiagnostics
| where Category == "ApplicationGatewayAccessLog"
````
🧾 Sample output columns from Application Gateway logs:
TimeGenerated [UTC]: Timestamp when the log entry was generated. Useful for time filtering.
ResourceId: Full Azure resource path. Helps identify the exact resource emitting the log.
Category: Log category, e.g., ApplicationGatewayAccessLog. Used to filter log types.
ResourceGroup: Azure resource group name. Useful for scoping queries.
SubscriptionId: Azure subscription ID. Can be used for multi-subscription filtering.
ResourceProvider: Azure resource provider, e.g., MICROSOFT.NETWORK.
Resource: Name of the resource (e.g., Application Gateway name).
ResourceType: Type of the resource, e.g., APPLICATIONGATEWAYS.
OperationName: Operation performed, e.g., ApplicationGatewayAccess.
requestUri_s: The URI path of the request. Useful for filtering specific API endpoints.
userAgent_s: User agent string from the client. Can help identify source applications.
ruleName_s: Name of the rule that matched the request.
httpMethod_s: HTTP method used (GET, POST, etc.).
instanceId_s: Instance of the gateway that handled the request.
httpVersion_s: HTTP version used in the request.
clientIP_s: IP address of the client making the request. Useful for source tracking.
host_s: Host header in the request. Can help identify virtual hosts.
requestQuery_s: Query string parameters in the request.
sslEnabled_s: Whether SSL was enabled for the request.
clientPort_d: Port number used by the client.

2. **""Show failed API calls to /my_api in the last 3 days and show only relevant fields""**
```kql
AzureDiagnostics
| where Category == "ApplicationGatewayAccessLog"
| where TimeGenerated >= ago(3d)
| extend URI=requestUri_s, status=httpStatus_d, method=httpMethod_s, sentBytes=sentBytes_d
| where status != 200
| where isempty(host_s)
| where requestUri_s == "/my_api"
| summarize count() by clientIP_s
```
🎯 Guidelines:
Use appropriate tables like AzureDiagnostics, SigninLogs, SecurityEvent, etc.
Apply time filters using TimeGenerated and the provided time range.
If the user query is already in KQL, return it as-is.
Do not include markdown formatting unless explicitly asked.
Respond with only the KQL query.
Return only the final KQL query.
"""