"""
Run from the repository root:
运行这个demo，需要首先把服务端启动起来
    uv run http_server.py
"""

import asyncio
from pydantic import AnyUrl
from mcp import ClientSession,types
from mcp.client.streamable_http import streamablehttp_client
from mcp.types import PromptReference, ResourceTemplateReference


async def main():
    # Connect to a streamable HTTP server
    async with streamablehttp_client("http://localhost:8001/mcp") as (
        read_stream,
        write_stream,
        _,
    ):
        # Create a session using the client streams
        async with ClientSession(read_stream, write_stream) as session:
            # Initialize the connection
            await session.initialize()
            # List available tools
            tools = await session.list_tools()
            print(f"Available tools: {[tool.name for tool in tools.tools]}")

            # 资源
            resource_content = await session.read_resource(AnyUrl("github://repos/main/python-sdk"))
            content_block = resource_content.contents[0]
            if isinstance(content_block, types.TextResourceContents):
                print(f"Resource content: {content_block.text}")
                
            # Prompt
            prompts = await session.list_prompts()
            print("\nAvailable prompts:")
            for prompt in prompts.prompts:
                print(f"  - {prompt.name}")

            if prompts.prompts:
                prompt = await session.get_prompt(prompts.prompts[0].name, arguments={"language":"python", "code": "print('Hello, World!')"})
                print(f"Prompt result: {prompt.messages[0].content}")

if __name__ == "__main__":
    asyncio.run(main())