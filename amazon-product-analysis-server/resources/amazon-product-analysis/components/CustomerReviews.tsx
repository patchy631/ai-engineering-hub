import React, { useState } from "react";

interface CustomerReviewsProps {
    summary?: string;
    topReview?: string;
}

const QuoteIcon: React.FC = () => (
    <svg className="w-8 h-8 text-violet-300 dark:text-violet-700" viewBox="0 0 24 24" fill="currentColor">
        <path d="M14.017 21v-7.391c0-5.704 3.731-9.57 8.983-10.609l.995 2.151c-2.432.917-3.995 3.638-3.995 5.849h4v10h-9.983zm-14.017 0v-7.391c0-5.704 3.748-9.57 9-10.609l.996 2.151c-2.433.917-3.996 3.638-3.996 5.849h3.983v10h-9.983z" />
    </svg>
);

const ChatIcon: React.FC = () => (
    <svg className="w-5 h-5 text-violet-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
    </svg>
);

const StarIcon: React.FC = () => (
    <svg className="w-4 h-4 text-amber-400" viewBox="0 0 24 24" fill="currentColor">
        <path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z" />
    </svg>
);

const ChevronDownIcon: React.FC<{ expanded: boolean }> = ({ expanded }) => (
    <svg
        className={`w-4 h-4 transition-transform duration-200 ${expanded ? "rotate-180" : ""}`}
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
    >
        <polyline points="6 9 12 15 18 9" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
);

const MAX_REVIEW_LENGTH = 300;

export const CustomerReviews: React.FC<CustomerReviewsProps> = ({ summary, topReview }) => {
    const [isExpanded, setIsExpanded] = useState(false);

    if (!summary && !topReview) return null;

    const needsTruncation = topReview && topReview.length > MAX_REVIEW_LENGTH;
    const displayedReview = needsTruncation && !isExpanded
        ? topReview.slice(0, MAX_REVIEW_LENGTH).replace(/\s+\S*$/, "") + "..."
        : topReview;

    return (
        <div className="p-6 bg-surface border border-default rounded-2xl">
            <h4 className="text-lg font-semibold text-default mb-4 flex items-center gap-2">
                <ChatIcon />
                Customer Feedback
            </h4>

            {/* AI Summary */}
            {summary && (
                <div className="mb-4 p-4 bg-gradient-to-r from-violet-500/5 to-fuchsia-500/5 rounded-xl border border-violet-500/10">
                    <div className="flex items-center gap-2 mb-2">
                        <div className="flex items-center gap-1 px-2 py-0.5 bg-violet-500/10 rounded-full">
                            <svg className="w-3.5 h-3.5 text-violet-500" viewBox="0 0 24 24" fill="currentColor">
                                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" />
                            </svg>
                            <span className="text-xs font-medium text-violet-600 dark:text-violet-400">
                                Customer Insights
                            </span>
                        </div>
                    </div>
                    <p className="text-sm text-default leading-relaxed">
                        {summary}
                    </p>
                </div>
            )}

            {/* Top Review */}
            {topReview && (
                <div className="relative">
                    <div className="absolute -top-2 -left-1 opacity-50">
                        <QuoteIcon />
                    </div>
                    <div className="pl-8 pt-2">
                        <div className="flex items-center gap-1 mb-2">
                            {[...Array(5)].map((_, i) => (
                                <StarIcon key={i} />
                            ))}
                            <span className="ml-2 text-xs text-secondary">Top Review</span>
                        </div>
                        <p className="text-sm text-secondary leading-relaxed italic">
                            "{displayedReview}"
                        </p>
                        {needsTruncation && (
                            <button
                                onClick={() => setIsExpanded(!isExpanded)}
                                className="mt-2 flex items-center gap-1 text-xs font-medium text-violet-500 hover:text-violet-600 transition-colors"
                            >
                                {isExpanded ? "Show less" : "Read full review"}
                                <ChevronDownIcon expanded={isExpanded} />
                            </button>
                        )}
                    </div>
                </div>
            )}

            {/* Review source note */}
            <div className="mt-4 pt-4 border-t border-default flex items-center gap-2 text-xs text-secondary">
                <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <circle cx="12" cy="12" r="10" />
                    <path d="M12 16v-4M12 8h.01" strokeLinecap="round" />
                </svg>
                Sourced from verified Amazon customer reviews
            </div>
        </div>
    );
};