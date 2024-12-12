import json
import re
from urllib.parse import urljoin

import httpx
from mcp import McpError, types as types

from utils.config import Config
from brave_search_mcp.codes import CountryCode, LanguageCode

config = Config()

count_pattern = r"^\d+$"
freshness_pattern = r"^\d{4}-\d{2}-\d{2}to\d{4}-\d{2}-\d{2}$"


async def web_search(
    query: str,
    count: str = '10', # integer is not supported in MCP Inspector v0.3.0
    country: CountryCode = CountryCode.ALL_REGIONS.value,
    search_lang: LanguageCode = LanguageCode.ENGLISH.value,
    freshness: str | None = None,
) -> str:
    params = {
        "q": query,
        "count": _validate_count(count),
        "country": country,
        "search_lang": search_lang,
        "freshness": _validate_freshness(freshness) if freshness else None,
    }
    response = await _call_brave(
        url="/res/v1/web/search",
        params=params,
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


def _validate_count(count: str) -> str | None:
    if re.match(count_pattern, count):
        return count
    return None


def _validate_freshness(freshness: str) -> str | None:
    if re.match(freshness_pattern, freshness):
        return freshness
    return None


def _parse_search_results(data: dict) -> dict:
    search_results = data["web"]["results"]
    return {
        "results": [
            {
                "title": r["title"],
                "url": r["url"],
                "description": r["description"],
                "language": r["language"],
            }
            for r in search_results
        ]
    }
