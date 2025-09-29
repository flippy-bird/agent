import os
import asyncio
from dotenv import load_dotenv
from mcp_client import MCPClient

load_dotenv()

xhs_server_url = os.getenv("XHS_LOCAL_HOST_URL")

if __name__ == "__main__":
    async def main():
        xhs = MCPClient(xhs_server_url)
        try:
            await xhs.connect_server()
            tools = await xhs.get_tools()
            # for tool in tools:
            #     print(tool)
            # res = await xhs.call_tool("search_feeds", {"keyword":"杭州美食"})
            res = await xhs.call_tool("get_feed_detail", {"feed_id":"68747e8a0000000023005722", "xsec_token":"ABzu6xwYU9bQ9glCA4P-2YJ7x1h1-2oY8WR8GAvM_969k="})
            print(f"工具调用的结果是: {res}")
        finally:
            await xhs.cleanup()

    asyncio.run(main())