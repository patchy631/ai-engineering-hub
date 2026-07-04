import React, { useState } from "react";
import type { Specification } from "../types";

interface ProductSpecsProps {
    specifications: Specification[];
}

const SpecsIcon: React.FC = () => (
    <svg className="w-5 h-5 text-cyan-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
        <polyline points="14 2 14 8 20 8" />
        <line x1="16" y1="13" x2="8" y2="13" />
        <line x1="16" y1="17" x2="8" y2="17" />
        <polyline points="10 9 9 9 8 9" />
    </svg>
);

const ChevronDownIcon: React.FC<{ expanded: boolean }> = ({ expanded }) => (
    <svg
        className={`w-5 h-5 text-secondary transition-transform duration-200 ${expanded ? "rotate-180" : ""}`}
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
    >
        <polyline points="6 9 12 15 18 9" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
);

// Key specs to always show at top (prioritized)
const KEY_SPEC_TYPES = [
    "Brand",
    "Screen Size",
    "RAM Memory Installed Size",
    "Hard Disk Size",
    "CPU Model",
    "Processor Type",
    "Operating System",
    "Colour",
    "Resolution",
    "Item Weight",
];

const MAX_COLLAPSED_SPECS = 6;

export const ProductSpecs: React.FC<ProductSpecsProps> = ({ specifications }) => {
    const [isExpanded, setIsExpanded] = useState(false);

    if (!specifications || specifications.length === 0) return null;

    // Deduplicate specifications by type (keep first occurrence)
    const seen = new Set<string>();
    const uniqueSpecs = specifications.filter((spec) => {
        const key = spec.type.toLowerCase();
        if (seen.has(key)) return false;
        seen.add(key);
        return true;
    });

    // Sort: key specs first, then alphabetically
    const sortedSpecs = [...uniqueSpecs].sort((a, b) => {
        const aKeyIndex = KEY_SPEC_TYPES.findIndex(
            (key) => a.type.toLowerCase().includes(key.toLowerCase())
        );
        const bKeyIndex = KEY_SPEC_TYPES.findIndex(
            (key) => b.type.toLowerCase().includes(key.toLowerCase())
        );

        if (aKeyIndex !== -1 && bKeyIndex !== -1) return aKeyIndex - bKeyIndex;
        if (aKeyIndex !== -1) return -1;
        if (bKeyIndex !== -1) return 1;
        return a.type.localeCompare(b.type);
    });

    const displayedSpecs = isExpanded ? sortedSpecs : sortedSpecs.slice(0, MAX_COLLAPSED_SPECS);
    const hasMore = sortedSpecs.length > MAX_COLLAPSED_SPECS;

    return (
        <div className="p-6 bg-surface border border-default rounded-2xl">
            <h4 className="text-lg font-semibold text-default mb-4 flex items-center gap-2">
                <SpecsIcon />
                Specifications
                <span className="text-xs font-normal text-secondary ml-auto">
                    {sortedSpecs.length} specs
                </span>
            </h4>

            <div className="space-y-1">
                {displayedSpecs.map((spec, index) => (
                    <div
                        key={`${spec.type}-${index}`}
                        className={`flex items-start gap-3 py-3 ${index !== displayedSpecs.length - 1 ? "border-b border-default/50" : ""
                            }`}
                    >
                        <span className="text-sm text-secondary min-w-[140px] shrink-0">
                            {spec.type}
                        </span>
                        <span className="text-sm text-default font-medium break-words">
                            {spec.value}
                        </span>
                    </div>
                ))}
            </div>

            {/* Expand/Collapse button */}
            {hasMore && (
                <button
                    onClick={() => setIsExpanded(!isExpanded)}
                    className="mt-4 w-full flex items-center justify-center gap-2 py-2.5 bg-surface-elevated hover:bg-surface-elevated/80 rounded-xl border border-default transition-colors"
                >
                    <span className="text-sm font-medium text-secondary">
                        {isExpanded ? "Show less" : `Show all ${sortedSpecs.length} specifications`}
                    </span>
                    <ChevronDownIcon expanded={isExpanded} />
                </button>
            )}
        </div>
    );
};