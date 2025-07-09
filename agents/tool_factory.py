import importlib
import pkgutil
import os
from typing import List
from langchain_core.tools import BaseTool

def load_tools() -> List[BaseTool]:
    tool_list = []
    package = "agents.tools"
    tools_path = os.path.join(os.path.dirname(__file__), "tools")

    for finder, name, ispkg in pkgutil.iter_modules([tools_path]):
        full_module_name = f"{package}.{name}.tool"
        try:
            module = importlib.import_module(full_module_name)
            if hasattr(module, "get_tools"):
                tool_list.extend(module.get_tools())
        except ModuleNotFoundError as e:
            print(f"⚠️ Could not load tool {name}: {e}")
            continue

    return tool_list
