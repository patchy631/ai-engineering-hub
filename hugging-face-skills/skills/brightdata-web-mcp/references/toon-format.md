# TOON Format for Token Optimization

Reduce token consumption by 30-60% when processing structured data from Bright Data MCP.

## What is TOON?

**Token-Oriented Object Notation (TOON)** is a compact encoding for JSON data designed for LLM input. It minimizes token usage while maintaining full data fidelity.

TOON combines YAML's indentation-based structure with CSV-style tabular layout for uniform arrays.

> TOON is a **translation layer** - use JSON programmatically in your code, encode as TOON when passing data to LLMs.

---

## How TOON Works

### Standard JSON (Token-Expensive)

```json
{
  "products": [
    { "id": 1, "name": "Laptop", "price": 999 },
    { "id": 2, "name": "Mouse", "price": 29 },
    { "id": 3, "name": "Keyboard", "price": 79 }
  ]
}
```

### TOON (Token-Efficient)

```
products[3]{id,name,price}:
  1,Laptop,999
  2,Mouse,29
  3,Keyboard,79
```

- `[3]` declares array length (detects truncation)
- `{id,name,price}` declares fields once
- Each row contains comma-separated values

---

## Token Savings

| Format | Tokens | Savings |
|--------|--------|---------|
| JSON | ~235 | - |
| TOON | ~106 | ~55% |

---

## When to Use TOON

### Ideal Use Cases

| Data Type | Example | Savings |
|-----------|---------|---------|
| Product listings | E-commerce catalogs | 40-60% |
| User records | Flat profile data | 35-55% |
| Log entries | Structured logs | 45-60% |
| Search results | SERP data (flat) | 40-55% |
| Simple tables | Spreadsheet-like data | 50-65% |

### Avoid TOON When

- **Deeply nested data** - Complex hierarchical structures don't benefit
- **Non-uniform data** - Items with different/optional fields
- **Direct MCP responses** - Most `web_data_*` endpoints return nested JSON

---

## TOON with Bright Data MCP

### The Challenge

Bright Data's `web_data_*` endpoints return **nested, hierarchical JSON**:
- Product data with nested reviews, specs, variants
- LinkedIn profiles with nested experience, education, skills
- Instagram posts with nested comments, media

TOON works best on **flat, uniform** data.

### Solution: Flatten First

Post-process MCP responses to extract flat arrays before TOON encoding:

```javascript
import { encode } from '@toon-format/toon'

// Original nested MCP response
const mcpResponse = await callTool('web_data_amazon_product', { url })

// Flatten to key fields
function flattenProduct(product) {
  return {
    title: product.title,
    price: product.final_price,
    currency: product.currency,
    rating: product.rating,
    reviews: product.reviews_count,
    seller: product.seller_name,
    brand: product.brand,
    in_stock: product.is_available
  }
}

const flatProducts = mcpResponse.map(flattenProduct)
const toonOutput = encode({ products: flatProducts })
```

---

## Quick Start

### Installation

```bash
npm install @toon-format/toon
```

### Basic Usage

```javascript
import { encode, decode } from '@toon-format/toon'

const data = {
  products: [
    { id: 1, name: 'Laptop', price: 999 },
    { id: 2, name: 'Mouse', price: 29 },
    { id: 3, name: 'Keyboard', price: 79 }
  ]
}

// Encode to TOON for LLM input
const toonData = encode(data)

// Decode back to JSON (lossless)
const jsonData = decode(toonData)
```

### CLI Usage

```bash
# Convert JSON to TOON
npx @toon-format/cli input.json -o output.toon

# Convert TOON to JSON
npx @toon-format/cli input.toon -o output.json
```

---

## Practical Example: MCP to TOON Pipeline

```javascript
import { Client } from '@modelcontextprotocol/sdk/client/index.js'
import { SSEClientTransport } from '@modelcontextprotocol/sdk/client/sse.js'
import { encode } from '@toon-format/toon'

// Connect to Bright Data MCP
const transport = new SSEClientTransport(
  new URL('https://mcp.brightdata.com/sse?token=YOUR_API_TOKEN&groups=ecommerce')
)

const client = new Client({ name: 'toon-example', version: '1.0.0' })
await client.connect(transport)

// Fetch Amazon product
const result = await client.callTool(
  { name: 'web_data_amazon_product', arguments: { url: 'https://amazon.com/dp/B0EXAMPLE' } },
  undefined,
  { timeout: 120000 }
)

const mcpResponse = JSON.parse(result.content[0].text)

// Flatten for TOON
const flatProducts = mcpResponse.map(p => ({
  title: p.title,
  price: p.final_price,
  currency: p.currency,
  rating: p.rating,
  reviews: p.reviews_count,
  seller: p.seller_name,
  brand: p.brand,
  in_stock: p.is_available
}))

// Convert to TOON
const toonOutput = encode({ products: flatProducts })

// Use in LLM prompt (55% fewer tokens!)
const prompt = `Analyze this product data:\n\n${toonOutput}`
```

---

## Flatteners for Common MCP Data

```javascript
const flatteners = {
  amazon_product: (p) => ({
    title: p.title,
    price: p.final_price,
    original_price: p.initial_price,
    currency: p.currency,
    rating: p.rating,
    reviews: p.reviews_count,
    seller: p.seller_name,
    brand: p.brand,
    in_stock: p.is_available
  }),

  linkedin_profile: (p) => ({
    name: p.full_name,
    headline: p.headline,
    location: p.city,
    country: p.country,
    connections: p.connections_count,
    followers: p.followers_count,
    company: p.current_company_name,
    position: p.position
  }),

  instagram_post: (p) => ({
    caption: p.description?.substring(0, 100),
    likes: p.likes,
    comments: p.comments,
    posted: p.upload_date,
    author: p.channel
  })
}

// Usage
function mcpToToon(data, flattener, key = 'items') {
  const items = Array.isArray(data) ? data : [data]
  const flattened = items.map(flattener)
  return encode({ [key]: flattened })
}
```

---

## Summary

| Use TOON For | Avoid TOON For |
|--------------|----------------|
| Flat, uniform arrays | Deeply nested objects |
| Tabular data | Non-uniform structures |
| Large datasets with repeated schemas | Direct MCP responses |
| Post-processed, flattened MCP data | Complex hierarchical data |

**Key Insight:** TOON is powerful for token optimization, but requires flattening Bright Data MCP's nested responses first.

---

## Resources

- [TOON Specification](https://github.com/toon-format/spec)
- [TypeScript SDK](https://www.npmjs.com/package/@toon-format/toon)
- [TOON Website](https://toonformat.dev)
