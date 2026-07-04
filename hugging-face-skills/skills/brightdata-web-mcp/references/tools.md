# Bright Data MCP Tools Reference

Complete reference for all available MCP tools.

## Modes Overview

| Mode | Activation | Description |
|------|------------|-------------|
| Rapid (Free) | Default | Web search and basic scraping (5,000 req/month free) |
| Pro | `&pro=1` or `PRO_MODE=true` | All 60+ tools including structured data and browser |
| Groups | `&groups=<name>` or `GROUPS=<name>` | Domain-specific tool bundles |
| Custom | `&tools=<name>` or `TOOLS=<name>` | Cherry-pick individual tools |

> Note: `GROUPS` or `TOOLS` override `PRO_MODE` when specified.

## Available Groups

| Group ID | Description | Key Tools |
|----------|-------------|-----------|
| `ecommerce` | Retail & marketplace datasets | `web_data_amazon_product`, `web_data_walmart_product`, `web_data_google_shopping` |
| `social` | Social media & creator insights | `web_data_linkedin_posts`, `web_data_tiktok_posts`, `web_data_youtube_videos` |
| `browser` | Browser automation | `scraping_browser_*` tools |
| `finance` | Financial intelligence | `web_data_yahoo_finance_business` |
| `business` | Company & location data | `web_data_crunchbase_company`, `web_data_zoominfo_company_profile`, `web_data_zillow_properties_listing` |
| `research` | News & developer data | `web_data_github_repository_file`, `web_data_reuter_news` |
| `app_stores` | App store data | `web_data_google_play_store`, `web_data_apple_app_store` |
| `travel` | Travel information | `web_data_booking_hotel_listings` |
| `advanced_scraping` | Batch & AI extraction | `search_engine_batch`, `scrape_batch`, `extract` |

---

## Core Tools (Rapid Mode - Free)

### search_engine
Search Google, Bing, or Yandex.

```json
{
  "query": "search terms",
  "engine": "google",
  "cursor": null
}
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | string | Search query (required) |
| `engine` | string | `google`, `bing`, or `yandex` |
| `cursor` | string | Pagination token for next page |

**Returns:** JSON for Google, Markdown for Bing/Yandex

### scrape_as_markdown
Scrape any URL and return clean Markdown. Handles bot protection automatically.

```json
{
  "url": "https://example.com/page"
}
```

---

## Advanced Scraping Tools (Pro / advanced_scraping)

### search_engine_batch
Run up to 10 searches in parallel.

```json
{
  "queries": ["query 1", "query 2", "query 3"],
  "engine": "google"
}
```

### scrape_batch
Scrape up to 10 URLs in one request.

```json
{
  "urls": ["https://example.com/1", "https://example.com/2"]
}
```

**Returns:** Array of URL/content pairs in Markdown

### scrape_as_html
Scrape and return raw HTML. Use when you need element structure.

```json
{
  "url": "https://example.com/page"
}
```

### extract
Scrape page and extract structured JSON using AI.

```json
{
  "url": "https://example.com/product",
  "prompt": "Extract: product_name, price, rating, reviews_count"
}
```

### session_stats
Report tool usage during the current MCP session.

```json
{}
```

---

## Browser Automation Tools (Pro / browser)

Use when content requires JavaScript rendering or user interaction.

### scraping_browser_navigate
Open or reuse a browser session and navigate to URL.

```json
{
  "url": "https://example.com"
}
```

### scraping_browser_go_back
Navigate back to previous page.

```json
{}
```

**Returns:** New URL and title

### scraping_browser_go_forward
Navigate forward to next page.

```json
{}
```

**Returns:** New URL and title

### scraping_browser_snapshot
Capture ARIA snapshot with element refs for interaction.

```json
{}
```

**Returns:** List of interactive elements with refs

### scraping_browser_click_ref
Click element by ref from snapshot.

```json
{
  "ref": "element-ref-123",
  "description": "Login button"
}
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `ref` | string | Element ref from snapshot (required) |
| `description` | string | Human-readable description (required) |

### scraping_browser_type_ref
Type into an input field.

```json
{
  "ref": "input-ref-456",
  "text": "search query",
  "submit": true
}
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `ref` | string | Element ref from snapshot (required) |
| `text` | string | Text to type (required) |
| `submit` | boolean | Press Enter after typing |

### scraping_browser_screenshot
Capture page screenshot.

```json
{
  "full_page": false
}
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `full_page` | boolean | Capture full scrollable page |

### scraping_browser_wait_for_ref
Wait for element to appear.

```json
{
  "ref": "element-ref",
  "timeout": 5000
}
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `ref` | string | Element ref to wait for (required) |
| `timeout` | number | Timeout in milliseconds |

### scraping_browser_scroll
Scroll to bottom of current page.

```json
{}
```

### scraping_browser_scroll_to_ref
Scroll until element is in view.

```json
{
  "ref": "element-ref"
}
```

### scraping_browser_get_text
Get text content from page body.

```json
{}
```

### scraping_browser_get_html
Get full HTML content.

```json
{
  "full_page": false
}
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `full_page` | boolean | Include head/script tags |

### scraping_browser_network_requests
List network requests since page load.

```json
{}
```

**Returns:** HTTP method, URL, and response status for each request

---

## E-commerce Tools (Pro / ecommerce)

### web_data_amazon_product
Get structured Amazon product data.

```json
{
  "url": "https://www.amazon.com/dp/B0EXAMPLE123"
}
```

**Requires:** URL containing `/dp/`

### web_data_amazon_product_reviews
Get structured Amazon product reviews.

```json
{
  "url": "https://www.amazon.com/dp/B0EXAMPLE123"
}
```

### web_data_amazon_product_search
Get Amazon search results.

```json
{
  "keyword": "wireless mouse",
  "url": "https://www.amazon.com"
}
```

**Note:** Limited to first page of results

### web_data_walmart_product
Get structured Walmart product data.

```json
{
  "url": "https://www.walmart.com/ip/12345"
}
```

**Requires:** URL containing `/ip/`

### web_data_walmart_seller
Get structured Walmart seller data.

```json
{
  "url": "https://www.walmart.com/seller/12345"
}
```

### web_data_ebay_product
Get structured eBay product data.

```json
{
  "url": "https://www.ebay.com/itm/12345"
}
```

### web_data_google_shopping
Get structured Google Shopping data.

```json
{
  "url": "https://www.google.com/shopping/product/12345"
}
```

### web_data_homedepot_products
Get structured Home Depot product data.

```json
{
  "url": "https://www.homedepot.com/p/12345"
}
```

### web_data_bestbuy_products
Get structured Best Buy product data.

```json
{
  "url": "https://www.bestbuy.com/site/12345"
}
```

### web_data_etsy_products
Get structured Etsy product data.

```json
{
  "url": "https://www.etsy.com/listing/12345"
}
```

### web_data_zara_products
Get structured Zara product data.

```json
{
  "url": "https://www.zara.com/product/12345"
}
```

---

## Social Media Tools (Pro / social)

### LinkedIn

| Tool | Input | Description |
|------|-------|-------------|
| `web_data_linkedin_person_profile` | LinkedIn profile URL | Person profile data |
| `web_data_linkedin_company_profile` | LinkedIn company URL | Company profile data |
| `web_data_linkedin_job_listings` | LinkedIn jobs URL | Job listings data |
| `web_data_linkedin_posts` | LinkedIn post URL | Post data |
| `web_data_linkedin_people_search` | LinkedIn search URL | People search results |

### Instagram

| Tool | Input | Description |
|------|-------|-------------|
| `web_data_instagram_profiles` | Instagram profile URL | Profile data |
| `web_data_instagram_posts` | Instagram post URL | Post data |
| `web_data_instagram_reels` | Instagram reel URL | Reel data |
| `web_data_instagram_comments` | Instagram URL | Comments data |

### Facebook

| Tool | Input | Description |
|------|-------|-------------|
| `web_data_facebook_posts` | Facebook post URL | Post data |
| `web_data_facebook_marketplace_listings` | Marketplace listing URL | Listing data |
| `web_data_facebook_company_reviews` | Facebook company URL | Company reviews |
| `web_data_facebook_events` | Facebook event URL | Event data |

### TikTok

| Tool | Input | Description |
|------|-------|-------------|
| `web_data_tiktok_profiles` | TikTok profile URL | Profile data |
| `web_data_tiktok_posts` | TikTok post URL | Post data |
| `web_data_tiktok_shop` | TikTok Shop URL | Shop product data |
| `web_data_tiktok_comments` | TikTok video URL | Comments data |

### Other Platforms

| Tool | Input | Description |
|------|-------|-------------|
| `web_data_x_posts` | X/Twitter post URL | Post data |
| `web_data_youtube_videos` | YouTube video URL | Video metadata |
| `web_data_youtube_profiles` | YouTube channel URL | Channel profile |
| `web_data_youtube_comments` | YouTube video URL | Video comments |
| `web_data_reddit_posts` | Reddit post URL | Post data |

---

## Business Tools (Pro / business)

### web_data_crunchbase_company
Get structured Crunchbase company data.

```json
{
  "url": "https://www.crunchbase.com/organization/example"
}
```

### web_data_zoominfo_company_profile
Get structured ZoomInfo company data.

```json
{
  "url": "https://www.zoominfo.com/c/example"
}
```

### web_data_google_maps_reviews
Get structured Google Maps reviews.

```json
{
  "url": "https://www.google.com/maps/place/example",
  "days_limit": 3
}
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `url` | string | Google Maps URL (required) |
| `days_limit` | number | Limit reviews to last N days (default: 3) |

### web_data_zillow_properties_listing
Get structured Zillow property data.

```json
{
  "url": "https://www.zillow.com/homedetails/12345"
}
```

---

## Finance Tools (Pro / finance)

### web_data_yahoo_finance_business
Get structured Yahoo Finance company data.

```json
{
  "url": "https://finance.yahoo.com/quote/AAPL"
}
```

---

## Research Tools (Pro / research)

### web_data_reuter_news
Get structured Reuters news data.

```json
{
  "url": "https://www.reuters.com/article/example"
}
```

### web_data_github_repository_file
Get structured GitHub file data.

```json
{
  "url": "https://github.com/owner/repo/blob/main/file.js"
}
```

---

## App Store Tools (Pro / app_stores)

### web_data_google_play_store
Get structured Google Play app data.

```json
{
  "url": "https://play.google.com/store/apps/details?id=com.example"
}
```

### web_data_apple_app_store
Get structured Apple App Store data.

```json
{
  "url": "https://apps.apple.com/app/example/id12345"
}
```

---

## Travel Tools (Pro / travel)

### web_data_booking_hotel_listings
Get structured Booking.com hotel data.

```json
{
  "url": "https://www.booking.com/hotel/example"
}
```

---

## Response Format Notes

- **Search results:** JSON for Google, Markdown for Bing/Yandex
- **Structured data (`web_data_*`):** Nested JSON with platform-specific schema
- **Scraping:** Markdown (default) or HTML
- **Browser tools:** Varies by tool (text, HTML, screenshot, etc.)

For token-efficient processing of nested responses, see [toon-format.md](./toon-format.md).
