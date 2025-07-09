# agent/tools/base_tool.py

from abc import ABC, abstractmethod

class BaseTool(ABC):
    @abstractmethod
    def name(self) -> str:
        """Name used for identifying the tool."""
        pass

    @classmethod
    @abstractmethod
    def register_tool(cls):
        """
        Register and return an instance of the tool.
        Must be implemented by all subclasses.
        """
        pass

    @abstractmethod
    def run(self, **kwargs) -> str:
        """Run the tool with given kwargs and return response string."""
        pass
