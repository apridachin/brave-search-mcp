import asyncio
import logging

import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions

from brave_search_mcp.brave import web_search
from utils.config import Config

config = Config()
logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger("brave-search-mcp")
server = Server("brave-search-mcp")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="web_search",
            description="Search web",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                },
                "required": ["query"],
            },
        )
    ]


@server.call_tool()
async def handle_call_tool(
    name: str,
    arguments: dict,
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    tools = {
        "web_search": web_search,
    }
    if name not in tools.keys():
        raise ValueError(f"Unknown tool: {name}")

    if not arguments:
        raise ValueError("Missing arguments")

    query = arguments.get("query")

    if not query:
        raise ValueError("Missing query")

    tool_function = tools[name]
    result = await tool_function(query)

    return [
        types.TextContent(
            type="text",
            text=result,
        )
    ]


async def main():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="brave-search-mcp",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())