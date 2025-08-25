from mcp.server.fastmcp import FastMCP
from datetime import datetime
from mcp.types import (
    Completion,
    CompletionArgument,
    CompletionContext,
    PromptReference,
    ResourceTemplateReference,
)

mcp = FastMCP("StatefulServer")

###################### Tools ####################
@mcp.tool()
def get_current_time() -> str:
    """Get the current time"""
    return datetime.now().strftime("%H:%M:%S")

@mcp.tool()
def get_weather(city: str) -> str:
    """Get the weather for a given city"""
    # Replace this with your own weather API
    return f"现在{city}是晴天."

###################### resource ####################
@mcp.resource("github://repos/{owner}/{repo}")
def github_repo(owner: str, repo: str) -> str:
    """GitHub repository resource."""
    return f"Repository: {owner}/{repo}"

###################### prompt ####################
@mcp.prompt(description="Code review prompt")
def review_code(language: str, code: str) -> str:
    """Generate a code review."""
    return f"Review this {language} code:\n{code}"

###################### completion ####################
@mcp.completion()
async def handle_completion(
    ref: PromptReference | ResourceTemplateReference,
    argument: CompletionArgument,
    context: CompletionContext | None,
) -> Completion | None:
    """Provide completions for prompts and resources."""

    # Complete programming languages for the prompt
    if isinstance(ref, PromptReference):
        if ref.name == "review_code" and argument.name == "language":
            languages = ["python", "javascript", "typescript", "go", "rust"]
            return Completion(
                values=[lang for lang in languages if lang.startswith(argument.value)],
                hasMore=False,
            )

    # Complete repository names for GitHub resources
    if isinstance(ref, ResourceTemplateReference):
        if ref.uri == "github://repos/{owner}/{repo}" and argument.name == "repo":
            if context and context.arguments and context.arguments.get("owner") == "modelcontextprotocol":
                repos = ["python-sdk", "typescript-sdk", "specification"]
                return Completion(values=repos, hasMore=False)

    return None


if __name__ == "__main__":
    mcp.settings.port = 8001  ## 添加这个是因为默认端口是8000，被占用了，然后运行这个文件，也不报错，因此换成了8001
    mcp.run(transport="streamable-http")