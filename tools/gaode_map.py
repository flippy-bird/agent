import os
import asyncio
from dotenv import load_dotenv
from mcp import ClientSession
from typing import Optional
from contextlib import AsyncExitStack
from mcp.client.streamable_http import streamablehttp_client


load_dotenv()

class Map:
    def __init__(self):
        api_key = os.getenv("GAO_DE_MAP_KEY")
        self.server_url = f"https://mcp.amap.com/mcp?key={api_key}"
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()

    async def connect_server(self):
        read_stream, write_stream, _ = await self.exit_stack.enter_async_context(streamablehttp_client(self.server_url))
        self.session = await self.exit_stack.enter_async_context(ClientSession(read_stream, write_stream))
        await self.session.initialize()
    async def get_tools(self):
        if not self.session:
            raise ValueError("please connect to server first")
        
        response = await self.session.list_tools()
        tools = response.tools
        self.tools = [tool.name for tool in tools]
        avaliable_tools = [
            {
                "type":"function",
                "function": {
                    "name":tool.name,
                    "description":tool.description,
                    "parameters": tool.inputSchema 
                } 
             } for tool in tools
        ]

        return avaliable_tools
    
    async def call_tool(self, tool_name:str, tool_args:dict):
        if tool_name not in self.tools:
            raise ValueError(f"Tool {tool_name} not found")
        tool_result = await self.session.call_tool(tool_name, tool_args)
        return tool_result.content[0].text

    async def cleanup(self):
        await self.exit_stack.aclose()


if __name__ == "__main__":
    async def main():
        map = Map()
        try:
            await map.connect_server()
            tools = await map.get_tools()
            # for tool in tools:
            #     print(tool)
            res = await map.call_tool("maps_weather", {"city":"杭州"})
            print(f"工具调用的结果是: {res}")
        finally:
            await map.cleanup()

    asyncio.run(main())
