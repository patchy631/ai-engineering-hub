import React from "react";
import { getProxiedImageUrl } from "../utils";

interface ProductCardProps {
    title?: string;
    imageUrl?: string;
    price?: number;
    currency?: string;
    rating?: number;
    totalReviews?: number;
    mcpUrl?: string;
}

const StarIcon: React.FC<{ filled: boolean; half?: boolean }> = ({ filled, half }) => (
    <svg
        className="w-5 h-5"
        viewBox="0 0 24 24"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
    >
        {half ? (
            <>
                <defs>
                    <linearGradient id="halfStar">
                        <stop offset="50%" stopColor="#FBBF24" />
                        <stop offset="50%" stopColor="transparent" />
                    </linearGradient>
                </defs>
                <path
                    d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z"
                    fill="url(#halfStar)"
                    stroke="#FBBF24"
                    strokeWidth="1.5"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                />
            </>
        ) : (
            <path
                d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z"
                fill={filled ? "#FBBF24" : "transparent"}
                stroke={filled ? "#FBBF24" : "#9CA3AF"}
                strokeWidth="1.5"
                strokeLinecap="round"
                strokeLinejoin="round"
            />
        )}
    </svg>
);

const StarRating: React.FC<{ rating: number }> = ({ rating }) => {
    const stars = [];
    for (let i = 1; i <= 5; i++) {
        if (rating >= i) {
            stars.push(<StarIcon key={i} filled={true} />);
        } else if (rating >= i - 0.5) {
            stars.push(<StarIcon key={i} filled={false} half={true} />);
        } else {
            stars.push(<StarIcon key={i} filled={false} />);
        }
    }
    return <div className="flex items-center gap-0.5">{stars}</div>;
};

const formatPrice = (price: number, currency: string): string => {
    const currencySymbols: Record<string, string> = {
        USD: "$",
        INR: "₹",
        EUR: "€",
        GBP: "£",
        JPY: "¥",
    };
    const symbol = currencySymbols[currency] || currency;
    return `${symbol}${price.toLocaleString()}`;
};

const formatReviews = (count: number): string => {
    if (count >= 1000000) return `${(count / 1000000).toFixed(1)}M`;
    if (count >= 1000) return `${(count / 1000).toFixed(1)}K`;
    return count.toString();
};

export const ProductCard: React.FC<ProductCardProps> = ({
    title,
    imageUrl,
    price,
    currency,
    rating,
    totalReviews,
    mcpUrl,
}) => {
    // If we have absolutely no data, don't render anything
    if (!title && !imageUrl && price === undefined && rating === undefined) {
        return null;
    }

    const hasPrice = price !== undefined && price !== null && currency;
    const hasRating = rating !== undefined && rating !== null;
    const hasReviews = totalReviews !== undefined && totalReviews !== null;
    
    // Use proxied URL for Amazon images to avoid CORS issues
    const proxiedImageUrl = getProxiedImageUrl(imageUrl, mcpUrl);

    return (
        <div className="flex gap-6 p-6 bg-surface border border-default rounded-2xl">
            {/* Product Image - only show if we have an image URL */}
            {proxiedImageUrl && (
                <div className="relative shrink-0 w-32 h-32 rounded-xl overflow-hidden bg-white">
                    <img
                        src={proxiedImageUrl}
                        alt={title || "Product image"}
                        className="w-full h-full object-contain p-2"
                        onError={(e) => {
                            (e.target as HTMLImageElement).src =
                                "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='128' height='128' viewBox='0 0 24 24' fill='none' stroke='%239CA3AF' stroke-width='1' stroke-linecap='round' stroke-linejoin='round'%3E%3Crect x='3' y='3' width='18' height='18' rx='2' ry='2'%3E%3C/rect%3E%3Ccircle cx='8.5' cy='8.5' r='1.5'%3E%3C/circle%3E%3Cpolyline points='21 15 16 10 5 21'%3E%3C/polyline%3E%3C/svg%3E";
                        }}
                    />
                </div>
            )}

            {/* Product Info */}
            <div className="flex-1 min-w-0">
                {/* Title - only show if available */}
                {title && (
                    <h3 className="text-lg font-semibold text-default line-clamp-2 mb-3">
                        {title}
                    </h3>
                )}

                {/* Price - only show if available */}
                {hasPrice && (
                    <div className="text-2xl font-bold text-default mb-3">
                        {formatPrice(price, currency!)}
                    </div>
                )}

                {/* Rating - only show if available */}
                {hasRating && (
                    <div className="flex items-center gap-3">
                        <StarRating rating={rating} />
                        <span className="text-lg font-medium text-default">{rating.toFixed(1)}</span>
                        {hasReviews && (
                            <span className="text-secondary">
                                ({formatReviews(totalReviews)} reviews)
                            </span>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
};