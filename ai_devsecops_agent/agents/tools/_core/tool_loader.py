import importlib
import os
from agents.tools._core.base_tool import BaseTool

def load_tools():
    tools = []
    tools_dir = os.path.dirname(os.path.dirname(__file__))
    print(f"🔍 Scanning tools directory: {tools_dir}")
    for entry in os.scandir(tools_dir):
        if ( 
            entry.is_dir() 
            and not entry.name.startswith("__") 
            and not entry.name.startswith("_") 
            and entry.name != "__pycache__"
        ):
            print(f"🔍 Scanning directory: {entry.name}")
            try:
                module_path = f"agents.tools.{entry.name}.tool"
                print(f"🔍 Looking for tools in module: {module_path}")
                mod = importlib.import_module(module_path)
                print(f"✅ Successfully loaded module: {module_path}")
                for attr in dir(mod):
                    cls = getattr(mod, attr)

                    if (
                        isinstance(cls, type)
                        and issubclass(cls, BaseTool)
                        and cls is not BaseTool  # ✅ Skip the abstract base class
                        and hasattr(cls, "register_tool")
                    ):
                        print(f"🛠️ Found tool class: {cls.__name__}")
                        try:
                            tool_instance = cls.register_tool()
                            if tool_instance is None:
                                print(f"⚠️ {cls.__name__}.register_tool() returned None!")
                            else:
                                print(f"✅ Registered: {tool_instance.name()}")
                                tools.append(tool_instance)
                        except Exception as e:
                            print(f"❌ Error while calling register_tool() in {cls.__name__}: {e}")

            except Exception as e:
                print(f"⚠️ Could not load tool from {entry.name}: {e}")

    return tools
