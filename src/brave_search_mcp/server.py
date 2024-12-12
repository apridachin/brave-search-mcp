import asyncio
import logging

from jsonschema import validate, ValidationError
import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions

from brave_search_mcp.brave import web_search, freshness_pattern, count_pattern
from brave_search_mcp.codes import LanguageCode, CountryCode
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
            inputSchema=inputSchema,
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

    validate_arguments(arguments)
    tool_function = tools[name]
    result = await tool_function(**arguments)

    return [
        types.TextContent(
            type="text",
            text=result,
        )
    ]


inputSchema = {
    "type": "object",
    "properties": {
        "query": {"type": "string"},
        "count": {"type": "string", "pattern": count_pattern},
        "country": {"type": "string", "enum": [e for e in CountryCode]},
        "search_lang": {"type": "string", "enum":  [e for e in LanguageCode]},
        "freshness": {"type": "string", "pattern": freshness_pattern},
    },
    "required": ["query"],
}


def validate_arguments(arguments: dict):
    try:
        validate(instance=arguments, schema=inputSchema)
    except ValidationError as e:
        raise ValueError(f"Invalid arguments: {e.message}") from e


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