"""MCP 命令暴露模块."""

from nonebot import logger
from arclet.alconna import Alconna, Args, CommandMeta, Arparma, MultiVar
from nonebot_plugin_alconna import on_alconna, Match

from .client import MCPClient

mcp_cmd = Alconna(
    "mcp",
    Args["server", str]["tool", str]["args", MultiVar(str, "*")],
    meta=CommandMeta(
        description="调用 MCP 工具",
        usage="/mcp <server> <tool> [args...]",
        example="/mcp github search_issues nonebot2",
    ),
)

mcp_matcher = on_alconna(mcp_cmd, priority=10, block=True, use_cmd_start=True)

logger.debug(f"[MCP] Command registered: {mcp_cmd.path}")


@mcp_matcher.handle()
async def handle_mcp(
    result: Arparma,
    server: Match[str],
    tool: Match[str],
    args: Match[tuple[str, ...]],
) -> None:
    """处理 MCP 命令.

    用法: /mcp <server> <tool> [args...]
    示例: /mcp github search_issues nonebot2
    """
    if not server.available or not tool.available:
        await mcp_matcher.finish("用法: /mcp <server> <tool> [args]")

    server_name = server.result
    tool_name = tool.result
    tool_args_tuple = args.result if args.available else ()

    # 将参数组合为单个字符串传递给工具
    tool_args_str = " ".join(tool_args_tuple) if tool_args_tuple else ""

    logger.debug(f"[MCP] Command: server={server_name}, tool={tool_name}, args={tool_args_str!r}")

    client = MCPClient.get_instance()

    # 构造完整工具名
    full_tool_name = f"mcp__{server_name}__{tool_name}"

    # 调用工具，传递 input 参数
    result_text = await client.call_tool(full_tool_name, {"input": tool_args_str})

    await mcp_matcher.finish(result_text)
