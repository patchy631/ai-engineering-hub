# Bright Data MCP Usage Examples

Practical examples and community demos for common use cases.

---

## Quick Examples

### Web Search
```
Prompt: "Search for the latest AI news"
Tool: search_engine
Input: { "query": "latest AI news", "engine": "google" }
```

### Extract Flight Information
```
Prompt: "Extract all flight times departing from JFK Airport to Heathrow in the next 24 hours"
Tool: search_engine + scrape_as_markdown
```

### Company Research
```
Prompt: "Extract the Bright Data overview section from LinkedIn"
Tool: web_data_linkedin_company_profile
Input: { "url": "https://linkedin.com/company/bright-data" }
```

### Dynamic Site Interaction
```
Prompt: "Go to ebay.com, click the 'Shop by category' button, and extract all categories"
Tools: scraping_browser_navigate → scraping_browser_snapshot → scraping_browser_click_ref → scrape_as_markdown
```

---

## Workflow Patterns

### Research Agent Flow

```python
# 1. Search for relevant sources
search_results = await call_tool("search_engine", {
    "query": "AI developments 2026",
    "engine": "google"
})

# 2. Extract content from top results
for url in extract_urls(search_results):
    content = await call_tool("scrape_as_markdown", {"url": url})
    # Process content...

# 3. Summarize findings
```

### E-commerce Monitoring

```python
# Monitor product prices across platforms
products = [
    "https://amazon.com/dp/B0EXAMPLE1",
    "https://walmart.com/ip/12345",
]

for url in products:
    if "amazon" in url:
        data = await call_tool("web_data_amazon_product", {"url": url})
    elif "walmart" in url:
        data = await call_tool("web_data_walmart_product", {"url": url})
    
    # Track price changes...
```

### Social Media Analysis

```python
# Analyze LinkedIn company and employees
company = await call_tool("web_data_linkedin_company_profile", {
    "url": "https://linkedin.com/company/example"
})

# Search for employees
people = await call_tool("web_data_linkedin_people_search", {
    "url": "https://linkedin.com/search/results/people/?company=example"
})

# Get detailed profiles
for person_url in extract_profile_urls(people):
    profile = await call_tool("web_data_linkedin_person_profile", {
        "url": person_url
    })
```

### Browser Automation for Dynamic Sites

```python
# Navigate and interact with JavaScript-heavy site
await call_tool("scraping_browser_navigate", {
    "url": "https://example.com/app"
})

# Get page elements
snapshot = await call_tool("scraping_browser_snapshot", {})

# Find and click login button
login_ref = find_element(snapshot, "Login")
await call_tool("scraping_browser_click_ref", {
    "ref": login_ref,
    "description": "Login button"
})

# Wait for form
await call_tool("scraping_browser_wait_for_ref", {
    "ref": "email-input",
    "timeout": 5000
})

# Fill form
await call_tool("scraping_browser_type_ref", {
    "ref": "email-input",
    "text": "user@example.com",
    "submit": False
})

# Take screenshot
await call_tool("scraping_browser_screenshot", {
    "full_page": True
})
```

---

## Real-World Use Cases

### Price Comparison Agent

```python
async def compare_prices(product_name):
    """Compare product prices across multiple platforms."""
    
    # Search for product
    search = await call_tool("search_engine", {
        "query": f"{product_name} buy",
        "engine": "google"
    })
    
    prices = []
    
    # Check Amazon
    amazon_url = find_amazon_url(search)
    if amazon_url:
        data = await call_tool("web_data_amazon_product", {"url": amazon_url})
        prices.append({"platform": "Amazon", "price": data["final_price"]})
    
    # Check eBay
    ebay_url = find_ebay_url(search)
    if ebay_url:
        data = await call_tool("web_data_ebay_product", {"url": ebay_url})
        prices.append({"platform": "eBay", "price": data["price"]})
    
    return sorted(prices, key=lambda x: x["price"])
```

### News Aggregator

```python
async def aggregate_news(topic):
    """Collect and summarize news from multiple sources."""
    
    # Search multiple engines
    google_results = await call_tool("search_engine", {
        "query": f"{topic} news",
        "engine": "google"
    })
    
    bing_results = await call_tool("search_engine", {
        "query": f"{topic} news",
        "engine": "bing"
    })
    
    # Scrape top articles
    articles = []
    for url in get_unique_urls(google_results, bing_results)[:5]:
        content = await call_tool("scrape_as_markdown", {"url": url})
        articles.append(content)
    
    return articles
```

### Lead Generation

```python
async def find_leads(industry, location):
    """Find potential business leads."""
    
    # Search LinkedIn companies
    search_url = f"https://linkedin.com/search/results/companies/?keywords={industry}&geoUrn=%5B%22{location}%22%5D"
    
    companies = await call_tool("web_data_linkedin_company_profile", {
        "url": search_url
    })
    
    leads = []
    for company in companies:
        # Get company details
        profile = await call_tool("web_data_linkedin_company_profile", {
            "url": company["url"]
        })
        
        # Find decision makers
        people = await call_tool("web_data_linkedin_people_search", {
            "url": f"https://linkedin.com/search/results/people/?company={company['id']}&title=CEO%20OR%20CTO"
        })
        
        leads.append({
            "company": profile,
            "contacts": people
        })
    
    return leads
```

---

## Community Demos

### AI Voice Agent - Made $596 Overnight
- [GitHub Repo](https://github.com/llSourcell/my_ai_intern)
- [YouTube Demo](https://www.youtube.com/watch?v=YGzT3sVdwdY)

Built an AI voice agent that automated sales calls using Bright Data for real-time web research.

### LangGraph with MCP Adapters
- [GitHub Repo](https://github.com/techwithtim/BrightDataMCPServerAgent)
- [YouTube Demo](https://www.youtube.com/watch?v=6DXuadyaJ4g)

Integration example showing LangGraph with Bright Data MCP for intelligent web agents.

### Researcher Agent with Google ADK
- [GitHub Repo](https://github.com/MeirKaD/MCP_ADK)
- [YouTube Demo](https://www.youtube.com/watch?v=r7WG6dXWdUI)

Google ADK agent that fetches real-time data for research tasks.

### Multi-Agent Job Finder
- [GitHub Repo](https://github.com/bitswired/jobwizard)
- [YouTube Demo](https://www.youtube.com/watch?v=45OtteCGFiI)

TypeScript multi-agent system for job searching using Bright Data MCP.

### Replacing Multiple MCP Servers
- [YouTube Demo](https://www.youtube.com/watch?v=0xmE0OJrNmg)

How to consolidate multiple web scraping MCP servers into one Bright Data instance.

### Real-time Website Scraping
- [YouTube Demo](https://www.youtube.com/watch?v=bL5JIeGL3J0)

Demonstrates scraping any website in real-time using Bright Data's AI MCP Server.

### Gemini CLI Integration
- [YouTube Demo](https://www.youtube.com/watch?v=FE1LChbgFEw)

Usage example with Google's Gemini CLI and Bright Data MCP.

---

## Sample Prompts

### Research & Information

```
"What are the top 5 trending AI tools right now? Search the web and summarize."

"Find the current stock price of Tesla and recent news about the company."

"Get the weather forecast for New York City for the next 7 days."
```

### E-commerce

```
"Compare prices for AirPods Pro across Amazon, Walmart, and Best Buy."

"Find the best-rated wireless keyboards under $100 on Amazon."

"Get product reviews for [URL] and summarize the common complaints."
```

### Social Media

```
"Get the latest posts from [LinkedIn company page] about their products."

"Find the most popular TikTok videos about [topic] from the past week."

"Extract the profile information for [Instagram username]."
```

### Business Intelligence

```
"Get company information for [company name] from Crunchbase."

"Find recent reviews for [business] on Google Maps."

"Get job listings from [company] on LinkedIn."
```

### Travel & Local

```
"Find hotel prices in Paris for next weekend on Booking.com."

"Get restaurant ratings near Times Square from Google Maps."

"Search for flights from LAX to JFK for next month."
```

---

## Best Practices

### 1. Choose the Right Tool

| Scenario | Recommended Tool |
|----------|------------------|
| General search | `search_engine` |
| Article content | `scrape_as_markdown` |
| Structured platform data | `web_data_*` |
| JavaScript sites | `scraping_browser_*` |
| Multiple URLs | `scrape_batch` |

### 2. Handle Errors Gracefully

```python
try:
    result = await call_tool("web_data_amazon_product", {"url": url})
except TimeoutError:
    # Fall back to general scraping
    result = await call_tool("scrape_as_markdown", {"url": url})
```

### 3. Optimize for Speed

```python
# Batch requests when possible
urls = ["https://example.com/1", "https://example.com/2"]
results = await call_tool("scrape_batch", {"urls": urls})

# Use structured tools for supported platforms (faster)
# web_data_amazon_product > scrape_as_markdown for Amazon
```

### 4. Respect Rate Limits

```python
# Monitor usage
stats = await call_tool("session_stats", {})
print(f"Requests made: {stats['total_requests']}")

# Add delays if needed
import asyncio
await asyncio.sleep(1)  # 1 second delay between requests
```

---

## Resources

- [Bright Data MCP GitHub](https://github.com/brightdata-com/brightdata-mcp)
- [MCP Documentation](https://docs.brightdata.com/ai/mcp-server/overview)
- [Smithery Playground](https://smithery.ai/server/@luminati-io/brightdata-mcp/tools)
- [Bright Data Blog](https://brightdata.com/blog/ai)
