import asyncio
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from mcp.client.streamable_http import streamablehttp_client
from mcp.shared.message import SessionMessage
from mcp.types import JSONRPCRequest

import os
from openai import OpenAI
from dotenv import load_dotenv
import json

load_dotenv()

class MCPClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.llm = OpenAI(
            api_key=os.environ["OPENAI_API_KEY"],
            base_url=os.environ["OPENAI_BASE_URL"],
        )

    # 连接本地的服务端
    async def connect_to_server(self, server_scritp_path:str):
        command = "python"
        server_params = StdioServerParameters(
            command=command,
            args=[server_scritp_path],
            env=None
        )

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport

        # 验证的代码：ref: https://github.com/modelcontextprotocol/python-sdk/issues/1100
        # await self.write.send(SessionMessage(message=JSONRPCRequest(jsonrpc="2.0", id=0, method="initialize", params={})))
        # msg = await self.stdio.receive()
        # print(msg)

        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

        await self.session.initialize()

        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])

    # 连接远程的服务端(通过http的方式)
    async def connect_to_http_server(self, http_server_url: str):
        read_stream, write_stream, _ = await self.exit_stack.enter_async_context(streamablehttp_client(http_server_url))

        self.session = await self.exit_stack.enter_async_context(ClientSession(read_stream, write_stream))

        await self.session.initialize()

        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])

    async def process_query(self, query: str) -> str:
        messages = [
            {"role":"user",
             "content":query}
        ]

        response = await self.session.list_tools()
        avaliable_tools = [
            {
                "type":"function",
                "function": {
                    "name":tool.name,
                    "description":tool.description,
                    "parameters": tool.inputSchema 
                } 
             } for tool in response.tools
        ]

        res = self.llm.chat.completions.create(
            model = "qwen-max",
            messages=messages,
            tools=avaliable_tools,
        )

        final_text = []

        while res.choices[0].message.tool_calls:
            tool_name = res.choices[0].message.tool_calls[0].function.name
            tool_args = res.choices[0].message.tool_calls[0].function.arguments
            try:
                tool_args = json.loads(tool_args)
            except:
                tool_args = {}
            tool_result = await self.session.call_tool(tool_name, tool_args)
            final_text.append(f"[Calling tool {tool_name} with args {tool_args}]")
            final_text.append(f"[Calling tool result: {tool_result.content[0].text}]")
            messages.append(res.choices[0].message)
            messages.append({"role":"tool",
                             "content":tool_result.content[0].text,
                             "tool_call_id":res.choices[0].message.tool_calls[0].id})
            
            res = self.llm.chat.completions.create(
                model = "qwen-max",
                messages=messages,
                tools=avaliable_tools,
            )
        
        final_text.append(res.choices[0].message.content)

        return "\n".join(final_text)
    
    async def chat_loop(self):
        print("\n MCP Client started.")
        print("Type your query to question or type 'exit' to quit.")

        while True:
            try:
                query = input("\nQuery: ").strip()
                if query.lower() == "quit":
                    break
                response = await self.process_query(query)
                print("\n" + response)
            except Exception as e:
                print(f"\nError: {str(e)}")

    async def cleanup(self):
        await self.exit_stack.aclose()

async def main():
    # if len(sys.argv) < 2:
    #     print("Usage: python client.py <path_to_server_script>")
    #     sys.exit(1)
    server_path = "/home/pan/Documents/2025/github/my_projects/agent/examples/mcp_demo/stdio_server.py"

    client = MCPClient()
    try:
        # await client.connect_to_server(server_path)  # 连接本地服务端
        await client.connect_to_http_server("http://localhost:8001/mcp")
        await client.chat_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    import sys
    asyncio.run(main())