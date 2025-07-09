from agents.router import get_router_agent

def main():
    agent = get_router_agent()

    while True:
        query = input("🧠 Ask your DevSecOps agent a question (type 'exit' to quit):\n🧑‍💻 You: ")
        if query.lower() in ["exit", "quit"]:
            break
        response = agent.invoke({"input": query})
        print(f"\n🤖 {response['output']}\n")

if __name__ == "__main__":
    main()
