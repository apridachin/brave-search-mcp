import json
from urllib.parse import urljoin

import httpx
from mcp import McpError, types as types

from utils.config import Config

config = Config()

async def web_search(query: str) -> str:
    response = await _call_brave(
        url="/res/v1/web/search",
        params={
            "q": query,
        }
    )
    data = response.json()
    results = _parse_search_results(data)
    return json.dumps(results)


async def _call_brave(url: str, params: dict | None = None) -> httpx.Response:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url=urljoin(config.BRAVE_URL, url),
                headers={
                    "X-Subscription-Token": f"{config.BRAVE_API_KEY}",
                    "Content-Type": "application/json",
                    "Accept-Encoding": "gzip",
                },
                params=params,
            )
            response.raise_for_status()

        return response

    except httpx.HTTPError as e:
        raise McpError(types.INTERNAL_ERROR, f"Brave API error: {str(e)}")


def _parse_search_results(data: dict) -> dict:
    search_results = data["web"]["results"]
    return {
        "results": [
            {
                "title": r["title"],
                "url": r["url"],
                "description": r["description"],
            } for r in search_results
        ]
    }
