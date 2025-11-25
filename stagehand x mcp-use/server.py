import asyncio
from mcp_use import MCPAgent, MCPClient
from langchain_openai import ChatOpenAI

async def main():
    client = MCPClient.from_config_file("mcp-config.json")
    
    # Create sessions first
    await client.create_all_sessions()
    
    # Discover available tools from MCP server
    tools = set()
    for name in client.get_server_names():
        session = client.get_session(name)
        for t in await session.list_tools():
            tools.add(str(getattr(t, "name", None) or getattr(t, "tool", None) or "unknown"))
    
    print("Available MCP tools:", sorted(tools))
    
    llm = ChatOpenAI(model="gpt-4o-mini")
    agent = MCPAgent(
        llm=llm,
        client=client,
        system_prompt="You can browse with Stagehand MCP tools and answer user queries.",
        memory_enabled=True,
        max_steps=20,
    )
    result = await agent.run("Go to example.com and extract the title")
    print(result)
    await client.close_all_sessions()

if __name__ == "__main__":
    asyncio.run(main())
