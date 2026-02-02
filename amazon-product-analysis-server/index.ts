import { MCPServer, object } from "mcp-use/server";
import { analyzeAmazonProduct } from "./resources/amazon-product-analysis/server.js";

const server = new MCPServer({
  name: "amazon-product-analysis-server",
  version: "1.0.0",
  description: "MCP server for Amazon product analysis",
  baseUrl: process.env.MCP_URL || "http://localhost:3000", // Full base URL (e.g., https://myserver.com)
  // favicon: "favicon.ico", // Uncomment and add your favicon to public/ folder
});

/**
 * AUTOMATIC UI WIDGET REGISTRATION
 * All React components in the `resources/` folder are automatically registered as MCP tools and resources.
 * Just export widgetMetadata with description and Zod schema, and mcp-use handles the rest!
 *
 * It will automatically add to your MCP server:
 * - server.tool('get-brand-info')
 * - server.resource('ui://widget/get-brand-info')
 *
 * See docs: https://docs.mcp-use.com/typescript/server/ui-widgets
 */

/**
 * Add here your standard MCP tools, resources and prompts
 */

// Image proxy endpoint to bypass CORS restrictions for Amazon images
server.get("/api/image-proxy", async (c) => {
  const imageUrl = c.req.query("url");

  if (!imageUrl) {
    return c.json({ error: "URL parameter is required" }, 400);
  }

  try {
    // Validate that the URL is from Amazon's CDN
    const url = new URL(imageUrl);
    const allowedHosts = [
      "m.media-amazon.com",
      "images-na.ssl-images-amazon.com",
      "images-eu.ssl-images-amazon.com",
      "images-fe.ssl-images-amazon.com",
      "ecx.images-amazon.com",
    ];

    if (!allowedHosts.some((host) => url.hostname.includes(host) || url.hostname.endsWith(".media-amazon.com"))) {
      return c.json({ error: "Only Amazon image URLs are allowed" }, 403);
    }

    // Fetch the image from Amazon
    const response = await fetch(imageUrl, {
      headers: {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
        "Referer": "https://www.amazon.com/",
      },
    });

    if (!response.ok) {
      return c.json({ error: "Failed to fetch image" }, 502);
    }

    // Get the content type and body
    const contentType = response.headers.get("content-type") || "image/jpeg";
    const imageBuffer = await response.arrayBuffer();

    // Return the image with appropriate headers
    return new Response(imageBuffer, {
      headers: {
        "Content-Type": contentType,
        "Cache-Control": "public, max-age=86400", // Cache for 24 hours
        "Access-Control-Allow-Origin": "*",
      },
    });
  } catch (error) {
    console.error("Error proxying image:", error);
    return c.json({ error: `Failed to proxy image: ${String(error)}` }, 500);
  }
});

// API endpoint for Amazon product analysis
server.get("/api/analyze-amazon-product", async (c) => {
  const url = c.req.query("url");
  const zipcode = c.req.query("zipcode");

  if (!url) {
    return c.json({ error: "URL parameter is required" }, 400);
  }

  try {
    const result = await analyzeAmazonProduct(url, zipcode);
    return c.json(result);
  } catch (error) {
    console.error("Error analyzing product:", error);
    return c.json({ error: `Failed to analyze product: ${String(error)}` }, 500);
  }
});

// Brand Info Tool - Returns brand information
server.tool(
  {
    name: "get-brand-info",
    description:
      "Get information about the brand, including company details, mission, and values",
  },
  async () => {
    return object({
      name: "mcp-use",
      tagline: "Build MCP servers with UI widgets in minutes",
      description:
        "mcp-use is a modern framework for building Model Context Protocol (MCP) servers with automatic UI widget registration, making it easy to create interactive AI tools and resources.",
      founded: "2025",
      mission:
        "To simplify the development of MCP servers and make AI integration accessible for developers",
      values: [
        "Developer Experience",
        "Simplicity",
        "Performance",
        "Open Source",
        "Innovation",
      ],
      contact: {
        website: "https://mcp-use.com",
        docs: "https://docs.mcp-use.com",
        github: "https://github.com/mcp-use/mcp-use",
      },
      features: [
        "Automatic UI widget registration",
        "React component support",
        "Full TypeScript support",
        "Built-in HTTP server",
        "MCP protocol compliance",
      ],
    });
  }
);

server.listen().then(() => {
  console.log(`Server running`);
});
