import React from "react";
import type { SellerInfo as SellerInfoType, Ranking } from "../types";

interface SellerInfoProps {
    seller?: SellerInfoType;
    rankings?: Ranking[];
    categories?: string[];
}

const StoreIcon: React.FC = () => (
    <svg className="w-5 h-5 text-teal-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
        <polyline points="9 22 9 12 15 12 15 22" />
    </svg>
);

const TrophyIcon: React.FC = () => (
    <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6" />
        <path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18" />
        <path d="M4 22h16" />
        <path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22" />
        <path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22" />
        <path d="M18 2H6v7a6 6 0 0 0 12 0V2Z" />
    </svg>
);

const ShippingIcon: React.FC = () => (
    <svg className="w-4 h-4 text-secondary" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <rect x="1" y="3" width="15" height="13" rx="1" />
        <polygon points="16 8 20 8 23 11 23 16 16 16 16 8" />
        <circle cx="5.5" cy="18.5" r="2.5" />
        <circle cx="18.5" cy="18.5" r="2.5" />
    </svg>
);

const TagIcon: React.FC = () => (
    <svg className="w-4 h-4 text-secondary" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z" />
        <line x1="7" y1="7" x2="7.01" y2="7" />
    </svg>
);

const getRankColor = (rank: number): { bg: string; text: string; badge: string } => {
    if (rank <= 10) {
        return {
            bg: "bg-gradient-to-r from-amber-400 to-yellow-500",
            text: "text-amber-900",
            badge: "🏆"
        };
    }
    if (rank <= 50) {
        return {
            bg: "bg-gradient-to-r from-slate-300 to-gray-400",
            text: "text-slate-800",
            badge: "🥈"
        };
    }
    if (rank <= 100) {
        return {
            bg: "bg-gradient-to-r from-amber-600 to-orange-700",
            text: "text-white",
            badge: "🥉"
        };
    }
    return {
        bg: "bg-surface-elevated",
        text: "text-default",
        badge: ""
    };
};

const formatRank = (rank: number): string => {
    if (rank >= 1000) {
        return `#${(rank / 1000).toFixed(1)}K`;
    }
    return `#${rank.toLocaleString()}`;
};

export const SellerInfo: React.FC<SellerInfoProps> = ({ seller, rankings, categories }) => {
    if (!seller && (!rankings || rankings.length === 0) && (!categories || categories.length === 0)) {
        return null;
    }

    return (
        <div className="p-6 bg-surface border border-default rounded-2xl">
            <h4 className="text-lg font-semibold text-default mb-4 flex items-center gap-2">
                <StoreIcon />
                Seller & Rankings
            </h4>

            <div className="space-y-4">
                {/* Seller details */}
                {seller && (
                    <div className="p-4 bg-surface-elevated rounded-xl">
                        <div className="space-y-2">
                            {seller.soldBy && (
                                <div className="flex items-center gap-2">
                                    <span className="text-xs text-secondary uppercase tracking-wide min-w-[70px]">
                                        Sold by
                                    </span>
                                    <span className="text-sm text-default font-medium">
                                        {seller.soldBy}
                                    </span>
                                </div>
                            )}
                            {seller.name && seller.name !== seller.soldBy && (
                                <div className="flex items-center gap-2">
                                    <span className="text-xs text-secondary uppercase tracking-wide min-w-[70px]">
                                        Seller
                                    </span>
                                    <span className="text-sm text-default">
                                        {seller.name}
                                    </span>
                                </div>
                            )}
                            {seller.shipsFrom && (
                                <div className="flex items-center gap-2">
                                    <span className="text-xs text-secondary uppercase tracking-wide min-w-[70px]">
                                        Ships from
                                    </span>
                                    <span className="text-sm text-default flex items-center gap-1.5">
                                        <ShippingIcon />
                                        {seller.shipsFrom}
                                    </span>
                                </div>
                            )}
                        </div>
                    </div>
                )}

                {/* Category Rankings */}
                {rankings && rankings.length > 0 && (
                    <div>
                        <div className="flex items-center gap-2 mb-3">
                            <TrophyIcon />
                            <span className="text-sm font-medium text-secondary">Best Sellers Rank</span>
                        </div>
                        <div className="space-y-2">
                            {rankings.map((ranking, index) => {
                                const colors = getRankColor(ranking.rank);
                                return (
                                    <div
                                        key={index}
                                        className="flex items-center gap-3 p-3 bg-surface-elevated rounded-lg"
                                    >
                                        <div className={`shrink-0 px-3 py-1.5 ${colors.bg} rounded-lg`}>
                                            <span className={`text-sm font-bold ${colors.text}`}>
                                                {colors.badge} {formatRank(ranking.rank)}
                                            </span>
                                        </div>
                                        <span className="text-sm text-secondary truncate">
                                            in {ranking.category}
                                        </span>
                                    </div>
                                );
                            })}
                        </div>
                    </div>
                )}

                {/* Categories breadcrumb */}
                {categories && categories.length > 0 && (
                    <div className="pt-4 border-t border-default">
                        <div className="flex items-center gap-2 mb-2">
                            <TagIcon />
                            <span className="text-xs text-secondary uppercase tracking-wide">Category</span>
                        </div>
                        <div className="flex flex-wrap items-center gap-1.5">
                            {categories.map((category, index) => (
                                <React.Fragment key={index}>
                                    <span className="px-2 py-1 bg-surface-elevated text-xs text-default rounded">
                                        {category}
                                    </span>
                                    {index < categories.length - 1 && (
                                        <svg className="w-3 h-3 text-secondary" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                            <polyline points="9 18 15 12 9 6" />
                                        </svg>
                                    )}
                                </React.Fragment>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};