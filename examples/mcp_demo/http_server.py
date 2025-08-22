from mcp.server.fastmcp import FastMCP
from datetime import datetime

mcp = FastMCP("StatefulServer")

@mcp.tool()
def get_current_time() -> str:
    """Get the current time"""
    return datetime.now().strftime("%H:%M:%S")

@mcp.tool()
def get_weather(city: str) -> str:
    """Get the weather for a given city"""
    # Replace this with your own weather API
    return f"现在{city}是晴天."

if __name__ == "__main__":
    mcp.settings.port = 8001  ## 添加这个是因为默认端口是8000，被占用了，然后运行这个文件，也不报错，因此换成了8001
    mcp.run(transport="streamable-http")