from mcp.server.fastmcp import FastMCP
import sys
from datetime import datetime

mcp = FastMCP("Demo")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@mcp.tool()
def get_current_time() -> str:
    """Get the current time"""
    return datetime.now().strftime("%H:%M:%S")

@mcp.tool()
def get_weather(city: str) -> str:
    """Get the weather for a given city"""
    # Replace this with your own weather API
    return f"现在{city}是晴天."

@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"

# Add a prompt
@mcp.prompt()
def greet_user(name: str, style: str = "friendly") -> str:
    """Generate a greeting prompt"""
    styles = {
        "friendly": "Please write a warm, friendly greeting",
        "formal": "Please write a formal, professional greeting",
        "casual": "Please write a casual, relaxed greeting",
    }

    return f"{styles.get(style, styles['friendly'])} for someone named {name}."

if __name__ == "__main__":
    print("Starting MCP server...", file=sys.stderr)
    mcp.run(transport="stdio")