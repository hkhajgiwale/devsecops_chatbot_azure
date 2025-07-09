# agents/tools/nsg_flow_logs/tool.py

import os
import json
import gzip
from typing import List, Optional
from datetime import datetime, timedelta
from dotenv import load_dotenv
from dateutil import parser as date_parser 

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

from langchain.docstore.document import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import AzureOpenAIEmbeddings
from langchain_core.tools import StructuredTool, Tool

from agents.tools.nsg_flow_logs.prompt_builder import NSGFlowLogsPromptBuilder
from agents.utils.time_parser import parse_time_range
from agents.tools.nsg_flow_logs.schema import NSGQueryInput

load_dotenv()

VECTOR_STORE_PATH = ".nsg_faiss_index"
DEFAULT_LOOKBACK_DAYS = int(os.getenv("DEFAULT_LOOKBACK_DAYS", 7))

embeddings = AzureOpenAIEmbeddings(
    model=os.getenv("AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT_NAME", "text-embedding-3-large"),
    api_version=os.getenv("AZURE_OPENAI_EMBEDDINGS_API_VERSION", "2024-02-01"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_EMBEDDINGS_API_KEY")
)

def parse_nsg_logs(max_files=20, start_time=None, end_time=None) -> List[dict]:
    storage_url = os.getenv("AZURE_STORAGE_ACCOUNT_URL")
    container_name = os.getenv("AZURE_STORAGE_CONTAINER")
    if not storage_url or not container_name:
        raise ValueError("Missing Azure Storage env vars.")

    client = BlobServiceClient(account_url=storage_url, credential=DefaultAzureCredential())
    container = client.get_container_client(container_name)
    blobs = sorted(container.list_blobs(), key=lambda b: b.last_modified, reverse=True)[:max_files]

    flows = []
    for blob in blobs:
        data = container.get_blob_client(blob.name).download_blob().readall()
        content = gzip.decompress(data).decode("utf-8") if blob.name.endswith(".gz") else data.decode("utf-8")
        log_json = json.loads(content)

        for record in log_json.get("records", []):
            record_time_str = record.get("time", None)
            record_time = date_parser.parse(record_time_str) if record_time_str else None

            if start_time and end_time and record_time:
                if not (start_time <= record_time <= end_time):
                    continue

            for outer in record.get("properties", {}).get("flows", []):
                for inner in outer.get("flows", []):
                    for t in inner.get("flowTuples", []):
                        s = t.split(",")
                        if len(s) < 8:
                            continue
                        flows.append({
                            "timestamp": record_time_str,
                            "srcIP": s[1],
                            "destIP": s[2],
                            "srcPort": int(s[3]),
                            "destPort": int(s[4]),
                            "protocol": s[5],
                            "direction": s[6],
                            "flowState": s[7]
                        })
    return flows

def flow_to_text(flow: dict) -> str:
    return (
        f"{flow.get('timestamp')} | "
        f"SRC: {flow['srcIP']}:{flow['srcPort']} → "
        f"DST: {flow['destIP']}:{flow['destPort']} | "
        f"{flow['protocol']} | "
        f"{'Inbound' if flow['direction'] == 'I' else 'Outbound'} | "
        f"{'Allowed' if flow['flowState'] == 'A' else 'Denied'}"
    )

def nsg_flow_logs_vector_search(query: str, time_range: Optional[str] = None) -> str:
    try:
        if not time_range:
            print(f"🕒 No time range provided. Defaulting to last {DEFAULT_LOOKBACK_DAYS} days.")
            start_time = datetime.utcnow() - timedelta(days=DEFAULT_LOOKBACK_DAYS)
            end_time = datetime.utcnow()
        else:
            start_time, end_time = parse_time_range(time_range)

        if os.path.exists(VECTOR_STORE_PATH):
            db = FAISS.load_local(VECTOR_STORE_PATH, embeddings, allow_dangerous_deserialization=True)
            results = db.similarity_search(query, k=5)
            if not results:
                return "No relevant results found in cached NSG logs."
            return "\n".join(doc.page_content for doc in results).strip()

        flows = parse_nsg_logs(start_time=start_time, end_time=end_time)
        if not flows:
            return "No NSG flow logs found for the given time range."

        prompt = NSGFlowLogsPromptBuilder(flows=flows, query=query).build_prompt()
        docs = [Document(page_content=prompt, metadata={})]

        raw_flows = [Document(page_content=flow_to_text(f), metadata=f) for f in flows]
        chunks = CharacterTextSplitter(chunk_size=512, chunk_overlap=0).split_documents(raw_flows)

        db = FAISS.from_documents(chunks, embeddings)
        db.save_local(VECTOR_STORE_PATH)

        results = db.similarity_search(query, k=5)
        if not results:
            return "No relevant results found after indexing NSG logs."

        return "\n".join(doc.page_content for doc in results).strip()
    except Exception as e:
        return f"Error querying NSG logs: {str(e)}"

def fallback_response(query: str) -> str:
    return f"I'm sorry, I couldn't understand your query: '{query}'. Please rephrase or check for typos."

fallback_tool = Tool(
    name="FallbackResponder",
    func=fallback_response,
    description="Handles queries that do not match any known tool or command."
)

def get_tools():
    return [
        StructuredTool.from_function(
            name="NSGFlowLogsVectorSearch",
            func=nsg_flow_logs_vector_search,
            description="Search Azure NSG logs with a query and optional time range like 'last 7 days'",
            args_schema=NSGQueryInput
        ),
        fallback_tool
    ]

# Preload vector store if needed
if not os.path.exists(VECTOR_STORE_PATH):
    print("⏳ Building NSG flow vector store...")
    flows = parse_nsg_logs()
    if flows:
        raw_flows = [Document(page_content=json.dumps(flow), metadata=flow) for flow in flows]
        chunks = CharacterTextSplitter(chunk_size=512, chunk_overlap=0).split_documents(raw_flows)
        db = FAISS.from_documents(chunks, embeddings)
        db.save_local(VECTOR_STORE_PATH)
        print(f"✅ Vector store built at {VECTOR_STORE_PATH}")
    else:
        print("⚠️ No flow logs found. Skipping vector index creation.")
