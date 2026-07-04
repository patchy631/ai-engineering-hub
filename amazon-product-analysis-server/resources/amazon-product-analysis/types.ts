import { z } from "zod";

// Input schema - what the widget receives as props (the MCP tool input)
export const propSchema = z.object({
    url: z
        .string()
        .url()
        .describe("Amazon product URL (must contain /dp/ or /gp/product/)"),
    zipcode: z
        .string()
        .optional()
        .describe("Optional ZIP code for location-specific pricing"),
});

export type AmazonProductAnalysisProps = z.infer<typeof propSchema>;

// Specification item schema
const specificationSchema = z.object({
    type: z.string(),
    value: z.string(),
});

// Delivery option schema
const deliverySchema = z.object({
    type: z.enum(["standard", "fast"]),
    text: z.string(),
    date: z.string().optional(),
});

// Seller info schema
const sellerInfoSchema = z.object({
    name: z.string(),
    shipsFrom: z.string().optional(),
    soldBy: z.string().optional(),
});

// Category ranking schema
const rankingSchema = z.object({
    category: z.string(),
    rank: z.number(),
});

// Output schema - the data structure returned by the API (what the widget displays)
// All fields are made optional to gracefully handle partial data from LLM
export const productAnalysisSchema = z.object({
    product: z.object({
        title: z.string().optional(),
        imageUrl: z.string().url().optional(),
        price: z.number().optional(),
        currency: z.string().optional(),
        rating: z.number().min(0).max(5).optional(),
        totalReviews: z.number().int().min(0).optional(),
        brand: z.string().optional(),
        availability: z.string().optional(),
    }).optional(),
    pricing: z.object({
        initialPrice: z.number().optional(),
        finalPrice: z.number().optional(),
        discount: z.string().optional(), // e.g., "-19%"
        savings: z.number().optional(),
        currency: z.string().optional(),
    }).optional(),
    features: z.array(z.string()).optional(),
    // New universal fields
    images: z.array(z.string().url()).optional(),
    specifications: z.array(specificationSchema).optional(),
    delivery: z.array(deliverySchema).optional(),
    seller: sellerInfoSchema.optional(),
    customerReview: z.object({
        summary: z.string().optional(),
        topReview: z.string().optional(),
    }).optional(),
    rankings: z.array(rankingSchema).optional(),
    categories: z.array(z.string()).optional(),
    stockQuantity: z.number().optional(),
});

export type ProductAnalysisData = z.infer<typeof productAnalysisSchema>;
export type Specification = z.infer<typeof specificationSchema>;
export type DeliveryOption = z.infer<typeof deliverySchema>;
export type SellerInfo = z.infer<typeof sellerInfoSchema>;
export type Ranking = z.infer<typeof rankingSchema>;