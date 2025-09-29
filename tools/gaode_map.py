import os
import asyncio
from dotenv import load_dotenv
from mcp_client import MCPClient

# 从tools目录加载.env文件
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))
gaode_map_key = os.getenv("GAO_DE_MAP_KEY")
gaode_server_url = f"https://mcp.amap.com/mcp?key={gaode_map_key}"

if __name__ == "__main__":
    async def main():
        map = MCPClient(gaode_server_url)
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
