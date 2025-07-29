# 🤖 DevSecOps Chatbot for Azure

A modular AI-powered chatbot that helps DevSecOps and security engineers interact with Azure security data using natural language. This bot supports querying **NSG flow logs**, **KQL logs**, and is extensible to new tools like Azure Policy, Defender, and more.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![License](https://img.shields.io/github/license/hkhajgiwale/devsecops_chatbot_azure)

---

## 🧠 Why This Project?

Cloud security data is scattered and complex — especially in Azure. Engineers often spend hours manually writing KQL, digging through logs, and interpreting configurations.

**This chatbot simplifies that**: ask questions like  
> “What traffic hit subnet X in the last 2 hours?”  
> “Analyze this KQL for risky IPs.”  

...and it responds with intelligent, actionable output — powered by custom agents and prompt engineering.

---

## 🏗️ Architecture Overview

```text
devsecops_chatbot_azure/
├── app.py                 # API entry point
├── main.py                # Optional script entry
├── requirements.txt       # Python dependencies
│
├── agents/
│   ├── memory.py          # In-memory context tracking
│   ├── router.py          # Routes user queries to tools
│   ├── tool_factory.py    # Registers all tools
│   ├── tools/
│   │   ├── kql/           # Kusto Query Language support
│   │   └── nsg_flow_logs/ # NSG flow log analysis
│   └── utils/
│       └── time_parser.py # Parses human-readable time
```

---

## 🧩 Supported Tools

| Tool           | Description                                   |
|----------------|-----------------------------------------------|
| `KQLTool`      | Executes Kusto queries, formats insights      |
| `NSGFlowTool`  | Analyzes NSG Flow Logs for traffic patterns   |

Each tool is modular and includes:
- `prompt_builder.py`: Template builder
- `schema.py`: Input validation
- `tool.py`: Logic for execution

---

## 🚀 Getting Started

### 📦 Prerequisites
- Python 3.9+
- OpenAI or Azure OpenAI API key (if integrating with LLM)
- Azure credentials (if connecting live)

### ⚙️ Installation

```bash
git clone https://github.com/hkhajgiwale/devsecops_chatbot_azure.git
cd devsecops_chatbot_azure
pip install -r requirements.txt
```

---

## 💡 How It Works

- User asks a natural language question
- `router.py` determines which tool fits best
- The selected tool uses a prompt to call the LLM or process data
- Response is returned in a human-readable format

Example:

```python
query = "Show NSG traffic for subnet-a over the last 3 hours"
result = Router().route(query)
print(result)
```

---

## 🛠️ Adding a New Tool

1. Create a new folder under `agents/tools/your_tool_name/`
2. Add:
   - `prompt_builder.py`
   - `schema.py`
   - `tool.py`
3. Register your tool in `tool_factory.py`
4. Add logic in `router.py` to route relevant queries

---

## 🔐 Security Use Cases

- Real-time traffic diagnostics using NSG logs
- Investigation of suspicious IP patterns via KQL
- Rapid RCA (root cause analysis) during incidents
- Future: Defender for Cloud integration, compliance checks

---

## 🧪 Sample Queries

```text
"Show denied traffic from Asia to subnet-x in the last 6 hours"
"Run this KQL and summarize the results"
"What was the inbound traffic pattern yesterday on app-nsg?"
```

---

## 🤝 Contributing

We welcome contributions! If you have ideas for new tools or improvements:

1. Fork this repo
2. Create a feature branch
3. Submit a pull request

For major changes, open an issue first to discuss.

---

## 📄 License

This project is licensed under the MIT License.

---

## 🙋‍♂️ Author

**Harsh Khajgiwale**  
Senior DevSecOps Engineer | AI x Security Researcher  
🔗 [LinkedIn](https://www.linkedin.com/in/hkhajgiwale) • [Blog](https://medium.com/@hkhajgiwale)

---
