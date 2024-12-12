# Kagi MCP server

MCP server that allows to search web using Brave Search API

## Components

### Resources

The server implements calls of [API methods](https://api.search.brave.com/app/documentation/web-search/get-started):
- Web Search

### Prompts

The server provides doesn't provide any prompts:

### Tools

The server implements several tools:
- web_search to search web

## Configuration

## Quickstart

### Install

#### Claude Desktop

On MacOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`

<details>
  <summary>Development/Unpublished Servers Configuration</summary>
  ```
  "mcpServers": {
    "brave-search-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "path_to_project",
        "run",
        "brave-search-mcp"
      ],
      "env": {
        "BRAVE_API_KEY": "YOUR API KEY"
      }
    }
  }
  ```
</details>

## Development

### Debugging

```bash
npx @modelcontextprotocol/inspector uv --directory path_to_project run brave-search-mcp
```