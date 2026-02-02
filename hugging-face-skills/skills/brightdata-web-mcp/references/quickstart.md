# Bright Data MCP Setup Guide

## Prerequisites

1. [Bright Data account](https://brightdata.com/cp/start) (free tier: 5,000 requests/month)
2. API token from [user settings](https://brightdata.com/cp/setting/users)
3. For local setup: [Node.js](https://nodejs.org/) installed

---

## Remote MCP (Recommended)

No installation required. Use the hosted server URL in your MCP client.

### Endpoints

**SSE (Server-Sent Events):**
```
https://mcp.brightdata.com/sse?token=YOUR_API_TOKEN
```

**Streamable HTTP:**
```
https://mcp.brightdata.com/mcp?token=YOUR_API_TOKEN
```

### With Pro Mode (All Tools)
```
https://mcp.brightdata.com/sse?token=YOUR_API_TOKEN&pro=1
```

### With Tool Groups
```
https://mcp.brightdata.com/sse?token=YOUR_API_TOKEN&groups=ecommerce,social
```

### With Custom Tools
```
https://mcp.brightdata.com/sse?token=YOUR_API_TOKEN&tools=scrape_as_markdown,web_data_linkedin_person_profile
```

### Combined Options
```
https://mcp.brightdata.com/sse?token=YOUR_API_TOKEN&groups=ecommerce&tools=extract
```

### Remote URL Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `token` | API token (required) | `token=abc123` |
| `pro` | Enable all Pro tools | `pro=1` |
| `groups` | Tool group IDs (comma-separated) | `groups=ecommerce,social` |
| `tools` | Individual tool names (comma-separated) | `tools=scrape_as_markdown` |
| `unlocker` | Custom web unlocker zone | `unlocker=my_zone` |
| `browser` | Custom browser zone | `browser=my_browser` |

---

## Local MCP (Self-hosted)

### Quick Start

```bash
npx @brightdata/mcp
```

Or install globally:

```bash
npm install -g @brightdata/mcp
brightdata-mcp
```

### With Environment Variables

```bash
API_TOKEN=<your-token> npx @brightdata/mcp
```

### Enable Pro Mode

```bash
API_TOKEN=<token> PRO_MODE=true npx @brightdata/mcp
```

### Enable Tool Groups

```bash
API_TOKEN=<token> GROUPS=ecommerce,social npx @brightdata/mcp
```

---

## Client Configuration Examples

### Claude Desktop / Claude Code

Add to `claude_desktop_config.json`:

**Location:**
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "brightdata": {
      "command": "npx",
      "args": ["-y", "@brightdata/mcp"],
      "env": {
        "API_TOKEN": "<your-token>"
      }
    }
  }
}
```

### Codex (OpenAI)

Add to `.codex/config.toml` in your project root:

```toml
[mcp_servers.brightdata]
command = "npx"
args = ["mcp-remote", "https://mcp.brightdata.com/mcp?token=YOUR_API_TOKEN"]
```

### Cursor

Go to: Settings → Gear Icon → Tools & Integrations → Add Custom MCP

```json
{
  "mcpServers": {
    "brightdata-mcp": {
      "command": "npx",
      "args": ["-y", "@brightdata/mcp"],
      "env": {
        "API_TOKEN": "<your-token>",
        "PRO_MODE": "true"
      }
    }
  }
}
```

### VS Code

Add to workspace or user settings:

```json
{
  "mcp.servers": {
    "brightdata": {
      "command": "npx",
      "args": ["-y", "@brightdata/mcp"],
      "env": {
        "API_TOKEN": "<your-token>"
      }
    }
  }
}
```

### Full Configuration Example

```json
{
  "mcpServers": {
    "Bright Data": {
      "command": "npx",
      "args": ["-y", "@brightdata/mcp"],
      "env": {
        "API_TOKEN": "<your-api-token>",
        "PRO_MODE": "true",
        "GROUPS": "browser,advanced_scraping",
        "TOOLS": "web_data_linkedin_person_profile,web_data_amazon_product",
        "RATE_LIMIT": "100/1h",
        "WEB_UNLOCKER_ZONE": "my_zone_name",
        "BROWSER_ZONE": "my_browser_zone"
      }
    }
  }
}
```

---

## Environment Variables (Local)

| Variable | Description | Default |
|----------|-------------|---------|
| `API_TOKEN` | Bright Data API token (required) | - |
| `PRO_MODE` | Enable all Pro tools | `false` |
| `GROUPS` | Comma-separated tool groups | - |
| `TOOLS` | Comma-separated individual tools | - |
| `RATE_LIMIT` | Request rate limit | `100/1h` |
| `WEB_UNLOCKER_ZONE` | Custom zone for web scraping | `mcp_unlocker` |
| `BROWSER_ZONE` | Custom zone for browser automation | `mcp_browser` |

### Available Groups

`ecommerce`, `social`, `browser`, `finance`, `business`, `research`, `app_stores`, `travel`, `advanced_scraping`

---

## Verify Setup

After configuration, test with a simple search:

```
Tool: search_engine
Input: { "query": "test query", "engine": "google" }
```

If successful, you'll receive structured search results.

---

## Troubleshooting

### "spawn npx ENOENT" Error

Your system cannot find `npx`. Use the full Node.js path:

**macOS/Linux:**
```json
{
  "command": "/usr/local/bin/node",
  "args": ["node_modules/@brightdata/mcp/index.js"]
}
```

**Windows:**
```json
{
  "command": "C:\\Program Files\\nodejs\\node.exe",
  "args": ["node_modules/@brightdata/mcp/index.js"]
}
```

Find your path with:
- macOS/Linux: `which node`
- Windows: `where node`

### Timeout Issues

- Increase timeout to 180 seconds in client settings
- Use specialized `web_data_*` tools when available (faster)
- Keep browser operations close together in time

### Authentication Issues

- Verify API token is valid at [user settings](https://brightdata.com/cp/setting/users)
- Check token has proper permissions
- Ensure no extra whitespace in configuration

---

## Next Steps

- [Tools Reference](./tools.md) - Complete tool documentation
- [Integrations](./integrations.md) - Framework-specific setup
- [TOON Format](./toon-format.md) - Token optimization
- [Examples](./examples.md) - Usage patterns
