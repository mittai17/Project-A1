import asyncio
import os
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from colorama import Fore, Style

# Config: List of MCP Servers (Stdio)
# Format: "name": {"command": "...", "args": [...], "env": {...}}
MCP_CONFIG_FILE = "mcp_config.json"

class MCPManager:
    def __init__(self):
        self.servers = {}
        self.tools = []
        self._load_config()

    def _load_config(self):
        if os.path.exists(MCP_CONFIG_FILE):
            with open(MCP_CONFIG_FILE, 'r') as f:
                self.servers = json.load(f)

    async def list_tools(self):
        """
        Connects to all servers and aggregates tools.
        Returns a list of tool definitions.
        """
        self.tools = []
        for name, config in self.servers.items():
            print(f"{Fore.BLUE}[MCP] Connecting to {name}...{Style.RESET_ALL}")
            try:
                server_params = StdioServerParameters(
                    command=config['command'],
                    args=config.get('args', []),
                    env={**os.environ, **config.get('env', {})}
                )
                
                async with stdio_client(server_params) as (read, write):
                    async with ClientSession(read, write) as session:
                        await session.initialize()
                        result = await session.list_tools()
                        for tool in result.tools:
                            # Tag tool with server name for routing
                            t_def = tool.model_dump()
                            t_def['server'] = name 
                            self.tools.append(t_def)
            except Exception as e:
                print(f"{Fore.RED}[MCP ERROR] {name}: {e}{Style.RESET_ALL}")
        return self.tools

    async def call_tool(self, server_name, tool_name, arguments):
        """
        Connects to specific server and executes tool.
        """
        config = self.servers.get(server_name)
        if not config:
            return f"Server {server_name} not found."

        try:
             server_params = StdioServerParameters(
                command=config['command'],
                args=config.get('args', []),
                env={**os.environ, **config.get('env', {})}
            )
             async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    result = await session.call_tool(tool_name, arguments)
                    return result.content[0].text
        except Exception as e:
            return f"Tool Execution Error: {e}"

# Global instance
manager = MCPManager()

if __name__ == "__main__":
    # Test
    # Create a dummy config if not exists
    if not os.path.exists(MCP_CONFIG_FILE):
        with open(MCP_CONFIG_FILE, "w") as f:
            json.dump({
                "filesystem": {
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-filesystem", "."]
                }
            }, f, indent=2)
            print("Created example mcp_config.json")
    
    tools = asyncio.run(manager.list_tools())
    print("\nAvailable Tools:")
    for t in tools:
        print(f"- {t['name']} ({t['server']}): {t['description']}")
