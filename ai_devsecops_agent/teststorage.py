from azure.identity import DefaultAzureCredential
import os

cred = DefaultAzureCredential()
token = cred.get_token("https://storage.azure.com/.default")
print(f"🔑 Authenticated as: {token.token[:20]}...")

