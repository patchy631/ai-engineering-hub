import React, { useState } from "react";

interface FeaturesProps {
    features: string[];
}

// Rotating gradient colors for feature badges
const featureGradients = [
    "from-violet-500 to-purple-600",
    "from-sky-500 to-blue-600",
    "from-emerald-500 to-teal-600",
    "from-amber-500 to-orange-600",
    "from-rose-500 to-pink-600",
];

const CheckIcon: React.FC = () => (
    <svg className="w-4 h-4 text-white shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
        <polyline points="20 6 9 17 4 12" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
);

const SparkleIcon: React.FC = () => (
    <svg className="w-5 h-5 text-amber-400" viewBox="0 0 24 24" fill="currentColor">
        <path d="M12 0L14.59 8.41L23 11L14.59 13.59L12 22L9.41 13.59L1 11L9.41 8.41L12 0Z" />
    </svg>
);

// Truncate long text to first sentence or max chars
const truncateText = (text: string, maxLength: number = 200): { truncated: string; isTruncated: boolean } => {
    // First try to get first sentence
    const firstSentenceMatch = text.match(/^[^.!?]*[.!?]/);
    if (firstSentenceMatch && firstSentenceMatch[0].length <= maxLength) {
        return {
            truncated: firstSentenceMatch[0],
            isTruncated: text.length > firstSentenceMatch[0].length
        };
    }

    // Otherwise truncate at word boundary
    if (text.length <= maxLength) {
        return { truncated: text, isTruncated: false };
    }

    const truncated = text.slice(0, maxLength).replace(/\s+\S*$/, "");
    return { truncated: truncated + "...", isTruncated: true };
};

interface FeatureItemProps {
    feature: string;
    gradient: string;
    index: number;
}

const FeatureItem: React.FC<FeatureItemProps> = ({ feature, gradient, index }) => {
    const [isExpanded, setIsExpanded] = useState(false);
    const { truncated, isTruncated } = truncateText(feature);

    return (
        <div
            className="group flex items-start gap-3 p-4 bg-surface-elevated rounded-xl border border-transparent hover:border-default transition-all duration-200"
        >
            {/* Gradient number badge */}
            <div className={`shrink-0 w-7 h-7 rounded-lg bg-gradient-to-br ${gradient} flex items-center justify-center shadow-lg`}>
                <span className="text-xs font-bold text-white">{index + 1}</span>
            </div>

            {/* Feature text */}
            <div className="flex-1 min-w-0">
                <p className="text-sm text-default leading-relaxed">
                    {isExpanded ? feature : truncated}
                </p>
                {isTruncated && (
                    <button
                        onClick={() => setIsExpanded(!isExpanded)}
                        className="mt-1.5 text-xs font-medium text-violet-500 hover:text-violet-600 transition-colors"
                    >
                        {isExpanded ? "Show less" : "Read more"}
                    </button>
                )}
            </div>

            {/* Check icon on hover */}
            <div className="shrink-0 opacity-0 group-hover:opacity-100 transition-opacity">
                <div className={`w-5 h-5 rounded-full bg-gradient-to-br ${gradient} flex items-center justify-center`}>
                    <CheckIcon />
                </div>
            </div>
        </div>
    );
};

const MAX_FEATURES_DISPLAY = 5;

export const Features: React.FC<FeaturesProps> = ({ features }) => {
    // Don't render if no features are available
    if (!features || features.length === 0) {
        return null;
    }

    const displayedFeatures = features.slice(0, MAX_FEATURES_DISPLAY);
    const remainingCount = features.length - MAX_FEATURES_DISPLAY;

    return (
        <div className="p-6 bg-surface border border-default rounded-2xl">
            <h4 className="text-lg font-semibold text-default mb-5 flex items-center gap-2">
                <SparkleIcon />
                Key Features
            </h4>

            <div className="space-y-3">
                {displayedFeatures.map((feature, index) => (
                    <FeatureItem
                        key={index}
                        feature={feature}
                        gradient={featureGradients[index % featureGradients.length]}
                        index={index}
                    />
                ))}
            </div>

            {/* Feature count badge */}
            <div className="mt-5 flex justify-center">
                <div className="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-violet-500/10 to-fuchsia-500/10 rounded-full border border-violet-500/20">
                    <svg className="w-4 h-4 text-violet-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
                        <polyline points="22 4 12 14.01 9 11.01" />
                    </svg>
                    <span className="text-xs font-medium text-violet-600 dark:text-violet-400">
                        {remainingCount > 0
                            ? `Top ${MAX_FEATURES_DISPLAY} of ${features.length} Features`
                            : `${features.length} Key Highlights`
                        }
                    </span>
                </div>
            </div>
        </div>
    );
};