from agents.agent_manager import AgentManager

if __name__ == "__main__":
    manager = AgentManager()
    manager.chat()  # Enters multi-tool chat mode with LLM-based tool routing
