import json
import gzip
import io
import os
from typing import List
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from agents.tools._core.base_tool import BaseTool
from agents.tools.nsg_flow_logs.prompt_builder import NSGFlowLogsPromptBuilder


class NSGFlowLogsTool(BaseTool):
    def __init__(self, storage_account_url: str, container_name: str):
        self.client = BlobServiceClient(account_url=storage_account_url, credential=DefaultAzureCredential())
        self.container = self.client.get_container_client(container_name)

    def name(self) -> str:
        return "NSG Flow Logs"

    @classmethod
    def register_tool(cls):
        # Defensive check
        storage_url = os.getenv("AZURE_STORAGE_ACCOUNT_URL")
        container = os.getenv("AZURE_STORAGE_CONTAINER")

        if not storage_url or not container:
            print("Missing required environment variables for NSG tool.")
            return None

        return cls(storage_account_url=storage_url, container_name=container)

    def run(self, **kwargs) -> str:
        max_files = kwargs.get("max_files", 5)
        flows = self.get_recent_flows(max_files=max_files)
        print(f"✅ Parsed {len(flows)} flow records from storage.")
        return NSGFlowLogsPromptBuilder(flows).build_prompt()

    def get_recent_flows(self, max_files: int = 5) -> List[dict]:
        flows = []
        print("🔍 Listing blobs in container...")
        blobs = list(self.container.list_blobs())
        print(f"📦 Found {len(blobs)} blobs.")

        blobs = sorted(blobs, key=lambda b: b.last_modified, reverse=True)[:max_files]

        for blob in blobs:
            if blob.name.endswith(".json") or blob.name.endswith(".json.gz"):
                blob_client = self.container.get_blob_client(blob.name)
                data = blob_client.download_blob().readall()

                if blob.name.endswith(".gz"):
                    with gzip.GzipFile(fileobj=io.BytesIO(data)) as f:
                        content = f.read().decode("utf-8")
                else:
                    content = data.decode("utf-8")

                log_json = json.loads(content)
                for record in log_json.get("records", []):
                    for outer_flow in record.get("properties", {}).get("flows", []):
                        for inner_flow in outer_flow.get("flows", []):
                            for tuple_str in inner_flow.get("flowTuples", []):
                                s = tuple_str.split(",")
                                if len(s) < 8:
                                    continue
                                flows.append({
                                    "srcIP": s[1],
                                    "destIP": s[2],
                                    "srcPort": int(s[3]),
                                    "destPort": int(s[4]),
                                    "protocol": s[5],
                                    "direction": s[6],
                                    "flowState": s[7]
                                })
        return flows
