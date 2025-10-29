from vindao_agents import Agent

agent = Agent.from_markdown("agents/SoftwareArchitect.md")

print("Starting analysis of the tools directory...\n")

for chunk, chunk_type in agent.instruct("Analyze the tools directory, including its structure, contents, potential improvements, and any architectural recommendations. Be thorough but concise."):
    if chunk_type == "reasoning":
        print(f"[Reasoning]: {chunk}")
    elif chunk_type == "content":
        print(chunk, end="")
    elif chunk_type == "tool":
        print(f"\n[Tool Call]: {chunk.name}\nResult: {chunk.result}\n")
    else:
        print(f"[Other]: {chunk} ({chunk_type})")

print("\nAnalysis complete.")