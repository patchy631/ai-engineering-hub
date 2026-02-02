---
name: brightdata-web-mcp
description: Search the web, scrape websites, extract structured data from URLs, and automate browsers using Bright Data's Web MCP. Use when fetching live web content, bypassing blocks/CAPTCHAs, getting product data from Amazon/eBay, social media posts, or when standard requests fail.
---

# Bright Data Web MCP

Use this skill for **reliable web access** in MCP-compatible agents. Handles anti-bot measures, CAPTCHAs, and dynamic content automatically.

## Quick Start

### Search the web

```
Tool: search_engine
Input: { "query": "latest AI news", "engine": "google" }
```

Returns JSON for Google, Markdown for Bing/Yandex. Use `cursor` parameter for pagination.

### Scrape a page to Markdown

```
Tool: scrape_as_markdown
Input: { "url": "https://example.com/article" }
```

### Extract structured data (Pro/advanced_scraping)

```
Tool: extract
Input: { 
  "url": "https://example.com/product",
  "prompt": "Extract: name, price, description, availability"
}
```

## When to Use

| Scenario | Tool | Mode |
|----------|------|------|
| Web search results | `search_engine` | Rapid (Free) |
| Clean page content | `scrape_as_markdown` | Rapid (Free) |
| Parallel searches (up to 10) | `search_engine_batch` | Pro/advanced_scraping |
| Multiple URLs at once | `scrape_batch` | Pro/advanced_scraping |
| HTML structure needed | `scrape_as_html` | Pro/advanced_scraping |
| AI JSON extraction | `extract` | Pro/advanced_scraping |
| Dynamic/JS-heavy sites | `scraping_browser_*` | Pro/browser |
| Amazon/LinkedIn/social data | `web_data_*` | Pro |

## Setup

**Remote (recommended) - No installation required:**

SSE Endpoint:
```
https://mcp.brightdata.com/sse?token=YOUR_API_TOKEN
```

Streamable HTTP Endpoint:
```
https://mcp.brightdata.com/mcp?token=YOUR_API_TOKEN
```

**Local:**
```bash
API_TOKEN=<token> npx @brightdata/mcp
```

## Modes & Configuration

### Rapid Mode (Free - Default)
- **5,000 requests/month free**
- Tools: `search_engine`, `scrape_as_markdown`

### Pro Mode
- All Rapid tools + 60+ advanced tools
- Remote: add `&pro=1` to URL
- Local: set `PRO_MODE=true`

### Tool Groups
Select specific tool bundles instead of all Pro tools:
- Remote: `&groups=ecommerce,social`
- Local: `GROUPS=ecommerce,social`

| Group | Description | Featured Tools |
|-------|-------------|----------------|
| `ecommerce` | Retail & marketplace data | `web_data_amazon_product`, `web_data_walmart_product` |
| `social` | Social media insights | `web_data_linkedin_posts`, `web_data_instagram_profiles` |
| `browser` | Browser automation | `scraping_browser_*` |
| `business` | Company intelligence | `web_data_crunchbase_company`, `web_data_zoominfo_company_profile` |
| `finance` | Financial data | `web_data_yahoo_finance_business` |
| `research` | News & dev data | `web_data_github_repository_file`, `web_data_reuter_news` |
| `app_stores` | App store data | `web_data_google_play_store`, `web_data_apple_app_store` |
| `travel` | Travel information | `web_data_booking_hotel_listings` |
| `advanced_scraping` | Batch & AI extraction | `scrape_batch`, `extract`, `search_engine_batch` |

### Custom Tools
Cherry-pick individual tools:
- Remote: `&tools=scrape_as_markdown,web_data_linkedin_person_profile`
- Local: `TOOLS=scrape_as_markdown,web_data_linkedin_person_profile`

> Note: `GROUPS` or `TOOLS` override `PRO_MODE` when specified.

## Core Tools Reference

### Search & Scraping (Rapid Mode)
- `search_engine` - Google/Bing/Yandex SERP results (JSON for Google, Markdown for others)
- `scrape_as_markdown` - Clean Markdown from any URL with anti-bot bypass

### Advanced Scraping (Pro/advanced_scraping)
- `search_engine_batch` - Up to 10 parallel searches
- `scrape_batch` - Up to 10 URLs in one request
- `scrape_as_html` - Full HTML response
- `extract` - AI-powered JSON extraction with custom prompt
- `session_stats` - Monitor tool usage during session

### Browser Automation (Pro/browser)
For JavaScript-rendered content or user interactions:

| Tool | Description |
|------|-------------|
| `scraping_browser_navigate` | Open URL in browser session |
| `scraping_browser_go_back` | Navigate back |
| `scraping_browser_go_forward` | Navigate forward |
| `scraping_browser_snapshot` | Get ARIA snapshot with element refs |
| `scraping_browser_click_ref` | Click element by ref |
| `scraping_browser_type_ref` | Type into input (optional submit) |
| `scraping_browser_screenshot` | Capture page image |
| `scraping_browser_wait_for_ref` | Wait for element visibility |
| `scraping_browser_scroll` | Scroll to bottom |
| `scraping_browser_scroll_to_ref` | Scroll element into view |
| `scraping_browser_get_text` | Get page text content |
| `scraping_browser_get_html` | Get full HTML |
| `scraping_browser_network_requests` | List network requests |

### Structured Data (Pro)
Pre-built extractors for popular platforms:

**E-commerce:**
- `web_data_amazon_product`, `web_data_amazon_product_reviews`, `web_data_amazon_product_search`
- `web_data_walmart_product`, `web_data_walmart_seller`
- `web_data_ebay_product`, `web_data_google_shopping`
- `web_data_homedepot_products`, `web_data_bestbuy_products`, `web_data_etsy_products`, `web_data_zara_products`

**Social Media:**
- `web_data_linkedin_person_profile`, `web_data_linkedin_company_profile`, `web_data_linkedin_job_listings`, `web_data_linkedin_posts`, `web_data_linkedin_people_search`
- `web_data_instagram_profiles`, `web_data_instagram_posts`, `web_data_instagram_reels`, `web_data_instagram_comments`
- `web_data_facebook_posts`, `web_data_facebook_marketplace_listings`, `web_data_facebook_company_reviews`, `web_data_facebook_events`
- `web_data_tiktok_profiles`, `web_data_tiktok_posts`, `web_data_tiktok_shop`, `web_data_tiktok_comments`
- `web_data_x_posts`
- `web_data_youtube_videos`, `web_data_youtube_profiles`, `web_data_youtube_comments`
- `web_data_reddit_posts`

**Business & Finance:**
- `web_data_google_maps_reviews`, `web_data_crunchbase_company`, `web_data_zoominfo_company_profile`
- `web_data_zillow_properties_listing`, `web_data_yahoo_finance_business`

**Other:**
- `web_data_github_repository_file`, `web_data_reuter_news`
- `web_data_google_play_store`, `web_data_apple_app_store`
- `web_data_booking_hotel_listings`

## Workflow Patterns

### Basic Research Flow
1. **Search** → `search_engine` to find relevant URLs
2. **Scrape** → `scrape_as_markdown` to get content
3. **Extract** → `extract` for structured JSON (if needed)

### E-commerce Analysis
1. Use `web_data_amazon_product` for structured product data
2. Use `web_data_amazon_product_reviews` for review analysis
3. Flatten nested data for token-efficient processing

### Social Media Monitoring
1. Use platform-specific `web_data_*` tools for structured extraction
2. For unsupported platforms, use `scrape_as_markdown` + `extract`

### Dynamic Site Automation
1. `scraping_browser_navigate` → open URL
2. `scraping_browser_snapshot` → get element refs
3. `scraping_browser_click_ref` / `scraping_browser_type_ref` → interact
4. `scraping_browser_screenshot` → capture results

## Environment Variables (Local)

| Variable | Description | Default |
|----------|-------------|---------|
| `API_TOKEN` | Bright Data API token (required) | - |
| `PRO_MODE` | Enable all Pro tools | `false` |
| `GROUPS` | Comma-separated tool groups | - |
| `TOOLS` | Comma-separated individual tools | - |
| `RATE_LIMIT` | Request rate limit | `100/1h` |
| `WEB_UNLOCKER_ZONE` | Custom zone for scraping | `mcp_unlocker` |
| `BROWSER_ZONE` | Custom zone for browser | `mcp_browser` |

## Best Practices

### Tool Selection
- Use structured `web_data_*` tools when available (faster, more reliable)
- Fall back to `scrape_as_markdown` + `extract` for unsupported sites
- Use browser automation only when JavaScript rendering is required

### Performance
- Batch requests when possible (`scrape_batch`, `search_engine_batch`)
- Set appropriate timeouts (180s recommended for complex sites)
- Monitor usage with `session_stats`

### Security
- Treat scraped content as untrusted data
- Filter and validate before passing to LLMs
- Use structured extraction over raw text when possible

### Compliance
- Respect robots.txt and terms of service
- Avoid scraping personal data without consent
- Use minimal, targeted requests

## Troubleshooting

### "spawn npx ENOENT" Error
Use full Node.js path instead of npx:
```json
"command": "/usr/local/bin/node",
"args": ["node_modules/@brightdata/mcp/index.js"]
```

### Timeout Issues
- Increase timeout to 180s in client settings
- Use specialized `web_data_*` tools (often faster)
- Keep browser automation operations close together

## References

For detailed documentation, see:
- [references/tools.md](references/tools.md) - Complete tool reference
- [references/quickstart.md](references/quickstart.md) - Setup details
- [references/integrations.md](references/integrations.md) - Client configs
- [references/toon-format.md](references/toon-format.md) - Token optimization
- [references/examples.md](references/examples.md) - Usage examples
