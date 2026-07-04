import { AppsSDKUIProvider } from "@openai/apps-sdk-ui/components/AppsSDKUIProvider";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { McpUseProvider, useWidget, type WidgetMetadata } from "mcp-use/react";
import React from "react";
import { Link } from "react-router";
import {
    ProductCard,
    PricingDeal,
    Features,
    ImageGallery,
    ProductSpecs,
    DeliveryInfo,
    CustomerReviews,
    SellerInfo,
} from "./components";
import { useProductAnalysis } from "./hooks";
import type { AmazonProductAnalysisProps } from "./types";
import { propSchema } from "./types";
import "../styles.css";

export const widgetMetadata: WidgetMetadata = {
    description:
        "Analyze any Amazon product by URL. Returns comprehensive product details including pricing, features, specifications, delivery options, customer reviews, and seller information.",
    inputs: propSchema,
    appsSdkMetadata: {
        "openai/widgetDescription": "Interactive Amazon product analysis widget with full product insights",
    },
};

const queryClient = new QueryClient();

const AmazonProductAnalysisContent: React.FC = () => {
    const { props, mcp_url } = useWidget<AmazonProductAnalysisProps>();
    const { url, zipcode } = props;

    // Fetch product analysis data using the custom hook
    const { data: analysis, isLoading, error } = useProductAnalysis(url, zipcode, mcp_url);

    return (
        <McpUseProvider debugger viewControls autoSize>
            <AppsSDKUIProvider linkComponent={Link}>
                <div className="relative bg-surface-elevated border border-default rounded-3xl overflow-hidden">
                    {/* Header gradient */}
                    <div className="absolute top-0 left-0 right-0 h-32 bg-gradient-to-b from-violet-500/10 via-fuchsia-500/5 to-transparent dark:from-violet-500/20 dark:via-fuchsia-500/10" />

                    <div className="relative p-6 space-y-6">
                        {/* Title Section */}
                        <div className="text-center mb-2">
                            <div className="inline-flex items-center gap-2 px-3 py-1 bg-violet-500/10 rounded-full mb-3">
                                <svg className="w-4 h-4 text-violet-500" viewBox="0 0 24 24" fill="currentColor">
                                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" />
                                </svg>
                                <span className="text-xs font-medium text-violet-500">Product Analysis</span>
                            </div>
                            <h2 className="text-xl font-bold text-default">Amazon Product Insights</h2>
                            <p className="text-sm text-secondary mt-1">
                                Comprehensive analysis powered by AI
                            </p>
                        </div>

                        {/* Loading State */}
                        {isLoading && (
                            <div className="flex flex-col items-center justify-center py-12 space-y-4">
                                <div className="relative w-16 h-16">
                                    <div className="absolute inset-0 border-4 border-violet-200 dark:border-violet-800 rounded-full" />
                                    <div className="absolute inset-0 border-4 border-violet-500 border-t-transparent rounded-full animate-spin" />
                                </div>
                                <p className="text-secondary">Analyzing product...</p>
                                <p className="text-xs text-secondary/60">Fetching data from Amazon via Bright Data</p>
                            </div>
                        )}

                        {/* Error State */}
                        {error && (
                            <div className="flex flex-col items-center justify-center py-12 space-y-4">
                                <div className="w-16 h-16 bg-red-100 dark:bg-red-900/20 rounded-full flex items-center justify-center">
                                    <svg className="w-8 h-8 text-red-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                        <circle cx="12" cy="12" r="10" />
                                        <line x1="15" y1="9" x2="9" y2="15" />
                                        <line x1="9" y1="9" x2="15" y2="15" />
                                    </svg>
                                </div>
                                <p className="text-red-500 font-medium">Failed to analyze product</p>
                                <p className="text-xs text-secondary max-w-xs text-center">{error.message}</p>
                            </div>
                        )}

                        {/* Success State - Show Analysis */}
                        {analysis && (
                            <>
                                {/* Product Card - shows available fields only */}
                                {analysis.product && (
                                    <ProductCard
                                        title={analysis.product.title}
                                        imageUrl={analysis.product.imageUrl}
                                        price={analysis.product.price}
                                        currency={analysis.product.currency}
                                        rating={analysis.product.rating}
                                        totalReviews={analysis.product.totalReviews}
                                        mcpUrl={mcp_url}
                                    />
                                )}

                                {/* Image Gallery - if multiple images available */}
                                {analysis.images && analysis.images.length > 1 && (
                                    <ImageGallery
                                        images={analysis.images}
                                        title={analysis.product?.title || "Product"}
                                        mcpUrl={mcp_url}
                                    />
                                )}

                                {/* Two column layout for Pricing and Features - only show if we have data */}
                                {(analysis.pricing || (analysis.features && analysis.features.length > 0)) && (
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                        {analysis.pricing && (
                                            <PricingDeal
                                                initialPrice={analysis.pricing.initialPrice}
                                                finalPrice={analysis.pricing.finalPrice}
                                                discount={analysis.pricing.discount}
                                                savings={analysis.pricing.savings}
                                                currency={analysis.pricing.currency}
                                            />
                                        )}
                                        {analysis.features && analysis.features.length > 0 && (
                                            <Features features={analysis.features} />
                                        )}
                                    </div>
                                )}

                                {/* Delivery and Seller Info Row */}
                                {(analysis.delivery || analysis.seller || analysis.rankings || analysis.categories) && (
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                        {analysis.delivery && analysis.delivery.length > 0 && (
                                            <DeliveryInfo
                                                delivery={analysis.delivery}
                                                availability={analysis.product?.availability}
                                                stockQuantity={analysis.stockQuantity}
                                            />
                                        )}
                                        {(analysis.seller || (analysis.rankings && analysis.rankings.length > 0) || (analysis.categories && analysis.categories.length > 0)) && (
                                            <SellerInfo
                                                seller={analysis.seller}
                                                rankings={analysis.rankings}
                                                categories={analysis.categories}
                                            />
                                        )}
                                    </div>
                                )}

                                {/* Customer Reviews */}
                                {analysis.customerReview && (analysis.customerReview.summary || analysis.customerReview.topReview) && (
                                    <CustomerReviews
                                        summary={analysis.customerReview.summary}
                                        topReview={analysis.customerReview.topReview}
                                    />
                                )}

                                {/* Product Specifications */}
                                {analysis.specifications && analysis.specifications.length > 0 && (
                                    <ProductSpecs specifications={analysis.specifications} />
                                )}
                            </>
                        )}

                        {/* Footer */}
                        <div className="flex items-center justify-center gap-2 pt-2 text-xs text-secondary">
                            <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
                            </svg>
                            <span>Data sourced via Bright Data • Analysis by AI</span>
                        </div>
                    </div>
                </div>
            </AppsSDKUIProvider>
        </McpUseProvider>
    );
};

const AmazonProductAnalysis: React.FC = () => {
    return (
        <QueryClientProvider client={queryClient}>
            <AmazonProductAnalysisContent />
        </QueryClientProvider>
    );
};

export default AmazonProductAnalysis;