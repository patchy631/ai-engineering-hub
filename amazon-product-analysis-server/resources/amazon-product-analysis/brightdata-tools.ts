import { tool, type Tool } from 'ai'
import { z } from 'zod'
import { bdclient } from '@brightdata/sdk'

type BrightDataTools = 'amazonProduct'

interface BrightDataToolsConfig {
    apiKey: string
    excludeTools?: BrightDataTools[]
}

export const brightDataTools = (
    config: BrightDataToolsConfig
): Partial<Record<BrightDataTools, Tool>> => {
    const client = new bdclient({
        apiKey: config.apiKey,
        autoCreateZones: true
    })

    const tools: Partial<Record<BrightDataTools, Tool>> = {
        amazonProduct: tool({
            description:
                'Get detailed Amazon product information including price, ratings, reviews, and specifications. Requires a valid Amazon product URL.',
            inputSchema: z.object({
                url: z
                    .string()
                    .url()
                    .describe('Amazon product URL (must contain /dp/ or /gp/product/)'),
                zipcode: z
                    .string()
                    .optional()
                    .describe('ZIP code for location-specific pricing and availability'),
            }),
            execute: async ({ url, zipcode }) => {
                try {
                    const result = await client.datasets.amazon.collectProducts(
                        [{ url, zipcode }],
                        {
                            format: 'json',
                            async: false
                        }
                    )
                    return JSON.stringify(result, null, 2)
                } catch (error) {
                    return `Error fetching Amazon product data: ${String(error)}`
                }
            },
        }),
    }

    // Remove excluded tools
    for (const toolName in tools) {
        if (config.excludeTools?.includes(toolName as BrightDataTools)) {
            delete tools[toolName as BrightDataTools]
        }
    }

    return tools
}