import { openai } from "@ai-sdk/openai";
import { generateText, generateObject, Output, stepCountIs } from "ai";
import { brightDataTools } from "./brightdata-tools.js";
import { productAnalysisSchema, type ProductAnalysisData } from "./types.js";

// Initialize Bright Data tools
const bdTools = brightDataTools({
    apiKey: process.env.BRIGHTDATA_API_KEY!,
});

/**
 * Fetches and analyzes Amazon product data using the same pattern as script.ts
 * This is SERVER-SIDE ONLY code - do not import in browser/widget code
 */
export async function analyzeAmazonProduct(
    url: string,
    zipcode?: string
): Promise<ProductAnalysisData> {
    // Step 1: Fetch product data using brightDataTools (same as script.ts)
    const fetchResult = await generateText({
        model: openai("gpt-4o"),
        tools: bdTools,

        // structured output happens here:
        // @ts-expect-error - Output.object API exists at runtime but types are outdated
        output: Output.object({
            // @ts-expect-error - name/description options exist at runtime
            name: "AmazonProductData",
            description: "Product fields extracted from tool output only.",
            schema: productAnalysisSchema,
        }),

        // structured output counts as a step, so leave room:
        stopWhen: stepCountIs(12),

        system: [
            "You extract Amazon product data by calling the provided tools.",
            "RULES:",
            "- Use tools to fetch data. Do not browse outside tools.",
            "- Fill fields ONLY if they are explicitly present in tool output.",
            "- Extract ALL available fields:",
            "  * Core: title, images (array), initial_price, final_price, discount, currency, rating, reviews_count, features",
            "  * Images: images array (all product image URLs)",
            "  * Specifications: product_details array (type/value pairs)",
            "  * Delivery: delivery array - classify as 'standard' or 'fast' type based on content",
            "  * Seller: seller_name, ships_from, buybox_seller",
            "  * Reviews: customer_says (summary), top_review (full text)",
            "  * Rankings: bs_rank, subcategory_rank array",
            "  * Categories: categories array",
            "  * Stock: availability, max_quantity_available",
            "- Price values must be numeric (no currency symbols/commas).",
            "- For delivery, mark as 'fast' if it mentions 'fastest', 'tomorrow', 'same day', or 'express'.",
        ].join("\n"),

        prompt: `Extract product data for this Amazon URL:\n${url}${zipcode ? `\nZipcode: ${zipcode}` : ""}`,
    });

    // Step 2: Structure data for widgets (same as script.ts)
    const result = await generateObject({
        model: openai("gpt-4o"),
        prompt: `Output this '${fetchResult.text}' to the product analysis schema.`,
        schema: productAnalysisSchema,
    });

    return result.object;
}