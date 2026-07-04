import React from "react";

interface PricingDealProps {
    initialPrice?: number;
    finalPrice?: number;
    discount?: string;
    savings?: number;
    currency?: string;
}

// Deal category types
type DealCategory = "hot" | "great" | "good" | "fair" | "minimal" | "none";

interface DealInfo {
    category: DealCategory;
    label: string;
    ribbonText: string;
    description: string;
    showRibbon: boolean;
    colors: {
        ribbon: string;
        accent: string;
        text: string;
        bg: string;
        border: string;
        bar: string;
    };
}

// Currency-specific thresholds for "significant" absolute savings
const significantSavingsThreshold: Record<string, number> = {
    USD: 50,
    INR: 2000,
    EUR: 45,
    GBP: 40,
    JPY: 5000,
};

const formatPrice = (price: number, currency: string): string => {
    const currencySymbols: Record<string, string> = {
        USD: "$",
        INR: "₹",
        EUR: "€",
        GBP: "£",
        JPY: "¥",
    };
    const symbol = currencySymbols[currency] || currency + " ";
    return `${symbol}${price.toLocaleString()}`;
};

/**
 * Categorizes a deal based on multiple factors:
 * - Discount percentage (primary factor)
 * - Absolute savings amount (secondary factor)
 * - Price point consideration (high-value items with moderate % off can still be good deals)
 */
const categorizeDeal = (
    discountPercent: number,
    savings: number,
    initialPrice: number,
    currency: string
): DealInfo => {
    const significantThreshold = significantSavingsThreshold[currency] || 50;

    // Calculate a "deal score" combining percentage and absolute value
    // Higher weight on percentage, but absolute savings can boost the score
    const absoluteSavingsBonus = Math.min(savings / significantThreshold, 2) * 5; // Max 10 points bonus
    const dealScore = discountPercent + absoluteSavingsBonus;

    // Hot Deal: 50%+ off OR 40%+ with significant absolute savings
    if (discountPercent >= 50 || (discountPercent >= 40 && savings >= significantThreshold * 2)) {
        return {
            category: "hot",
            label: "🔥 Hot Deal!",
            ribbonText: "HOT DEAL",
            description: "Exceptional savings - this is a steal!",
            showRibbon: true,
            colors: {
                ribbon: "from-rose-500 to-orange-500",
                accent: "text-rose-500",
                text: "text-rose-600 dark:text-rose-400",
                bg: "bg-rose-500/10",
                border: "border-rose-500/20",
                bar: "from-rose-400 to-orange-500",
            },
        };
    }

    // Great Deal: 30-49% off OR 20%+ with good absolute savings
    if (discountPercent >= 30 || (discountPercent >= 20 && savings >= significantThreshold * 1.5)) {
        return {
            category: "great",
            label: "Great Deal!",
            ribbonText: "GREAT DEAL",
            description: "Excellent price - worth grabbing!",
            showRibbon: true,
            colors: {
                ribbon: "from-emerald-500 to-teal-500",
                accent: "text-emerald-500",
                text: "text-emerald-600 dark:text-emerald-400",
                bg: "bg-emerald-500/10",
                border: "border-emerald-500/20",
                bar: "from-emerald-400 to-emerald-600",
            },
        };
    }

    // Good Deal: 15-29% off OR 10%+ with meaningful absolute savings
    if (discountPercent >= 15 || (discountPercent >= 10 && savings >= significantThreshold)) {
        return {
            category: "good",
            label: "Good Deal",
            ribbonText: "GOOD DEAL",
            description: "Decent savings on this item",
            showRibbon: true,
            colors: {
                ribbon: "from-sky-500 to-blue-500",
                accent: "text-sky-500",
                text: "text-sky-600 dark:text-sky-400",
                bg: "bg-sky-500/10",
                border: "border-sky-500/20",
                bar: "from-sky-400 to-blue-500",
            },
        };
    }

    // Fair Deal: 5-14% off - some savings but nothing special
    if (discountPercent >= 5 || dealScore >= 8) {
        return {
            category: "fair",
            label: "Fair Price",
            ribbonText: "SAVE",
            description: "Small savings available",
            showRibbon: false,
            colors: {
                ribbon: "from-amber-500 to-yellow-500",
                accent: "text-amber-500",
                text: "text-amber-600 dark:text-amber-400",
                bg: "bg-amber-500/10",
                border: "border-amber-500/20",
                bar: "from-amber-400 to-yellow-500",
            },
        };
    }

    // Minimal: 1-4% off - barely a discount
    if (discountPercent >= 1) {
        return {
            category: "minimal",
            label: "Minimal Savings",
            ribbonText: "",
            description: "Minor price reduction",
            showRibbon: false,
            colors: {
                ribbon: "from-gray-400 to-gray-500",
                accent: "text-gray-500",
                text: "text-gray-600 dark:text-gray-400",
                bg: "bg-gray-500/10",
                border: "border-gray-500/20",
                bar: "from-gray-400 to-gray-500",
            },
        };
    }

    // No Deal: No meaningful discount
    return {
        category: "none",
        label: "Regular Price",
        ribbonText: "",
        description: "No discount currently available",
        showRibbon: false,
        colors: {
            ribbon: "from-gray-300 to-gray-400",
            accent: "text-gray-400",
            text: "text-gray-500 dark:text-gray-400",
            bg: "bg-gray-500/5",
            border: "border-gray-500/10",
            bar: "from-gray-300 to-gray-400",
        },
    };
};

const CheckIcon: React.FC = () => (
    <svg className="w-5 h-5 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
        <polyline points="20 6 9 17 4 12" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
);

const InfoIcon: React.FC = () => (
    <svg className="w-5 h-5 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <circle cx="12" cy="12" r="10" />
        <path d="M12 16v-4M12 8h.01" strokeLinecap="round" />
    </svg>
);

export const PricingDeal: React.FC<PricingDealProps> = ({
    initialPrice,
    finalPrice,
    discount,
    savings,
    currency,
}) => {
    // If we don't have at least a final price and currency, don't render
    if (finalPrice === undefined || finalPrice === null || !currency) {
        return null;
    }

    const safeInitialPrice = initialPrice ?? finalPrice;
    const safeSavings = savings ?? 0;
    const safeDiscount = discount ?? "0%";
    
    const savingsPercent = Math.abs(parseFloat(safeDiscount.replace(/[^0-9.-]/g, ""))) || 0;
    const dealInfo = categorizeDeal(savingsPercent, safeSavings, safeInitialPrice, currency);
    const isGoodDealOrBetter = ["hot", "great", "good"].includes(dealInfo.category);

    return (
        <div className="p-6 bg-surface border border-default rounded-2xl overflow-hidden relative">
            {/* Deal ribbon - only show for actual deals */}
            {dealInfo.showRibbon && (
                <div className={`absolute -right-8 top-6 rotate-45 bg-gradient-to-r ${dealInfo.colors.ribbon} text-white text-xs font-bold py-1 px-10 shadow-lg`}>
                    {dealInfo.ribbonText}
                </div>
            )}

            <h4 className="text-lg font-semibold text-default mb-5 flex items-center gap-2">
                <svg className={`w-5 h-5 ${dealInfo.colors.accent}`} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
                Price Breakdown
            </h4>

            <div className="space-y-4">
                {/* Price comparison */}
                <div className="flex items-end gap-4">
                    <div className="flex flex-col">
                        <span className="text-xs text-secondary uppercase tracking-wide mb-1">You Pay</span>
                        <span className={`text-3xl font-bold ${dealInfo.colors.accent}`}>
                            {formatPrice(finalPrice, currency)}
                        </span>
                    </div>
                    {safeInitialPrice !== finalPrice && safeInitialPrice > 0 && (
                        <div className="flex flex-col pb-1">
                            <span className="text-xs text-secondary uppercase tracking-wide mb-1">Was</span>
                            <span className="text-xl text-secondary line-through">
                                {formatPrice(safeInitialPrice, currency)}
                            </span>
                        </div>
                    )}
                </div>

                {/* Savings bar - only show if there are actual savings */}
                {savingsPercent > 0 && safeSavings > 0 && (
                    <div className="relative pt-2">
                        <div className="flex justify-between text-sm mb-2">
                            <span className="text-secondary">Savings</span>
                            <span className={`font-semibold ${dealInfo.colors.accent}`}>
                                {formatPrice(safeSavings, currency)} ({safeDiscount})
                            </span>
                        </div>
                        <div className="h-3 bg-surface-elevated rounded-full overflow-hidden">
                            <div
                                className={`h-full bg-gradient-to-r ${dealInfo.colors.bar} rounded-full transition-all duration-1000 ease-out relative`}
                                style={{ width: `${Math.min(savingsPercent * 2, 100)}%` }}
                            >
                                {isGoodDealOrBetter && (
                                    <div className="absolute inset-0 bg-white/20 animate-pulse" />
                                )}
                            </div>
                        </div>
                    </div>
                )}

                {/* Deal assessment badge */}
                <div className={`flex items-center gap-2 p-3 ${dealInfo.colors.bg} border ${dealInfo.colors.border} rounded-xl`}>
                    <div className={`w-10 h-10 bg-gradient-to-br ${dealInfo.colors.ribbon} rounded-full flex items-center justify-center shrink-0`}>
                        {isGoodDealOrBetter ? <CheckIcon /> : <InfoIcon />}
                    </div>
                    <div>
                        <p className={`text-sm font-semibold ${dealInfo.colors.text}`}>
                            {dealInfo.label}
                        </p>
                        <p className="text-xs text-secondary">
                            {dealInfo.description}
                        </p>
                    </div>
                </div>

                {/* Deal score indicator for transparency - only show if there are savings */}
                {savingsPercent > 0 && safeSavings > 0 && (
                    <div className="flex items-center justify-between text-xs text-secondary pt-2 border-t border-default">
                        <span>Discount: {savingsPercent.toFixed(0)}%</span>
                        <span>Savings: {formatPrice(safeSavings, currency)}</span>
                    </div>
                )}
            </div>
        </div>
    );
};