import React from "react";
import type { DeliveryOption } from "../types";

interface DeliveryInfoProps {
    delivery: DeliveryOption[];
    availability?: string;
    stockQuantity?: number;
}

const TruckIcon: React.FC = () => (
    <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <rect x="1" y="3" width="15" height="13" rx="1" />
        <polygon points="16 8 20 8 23 11 23 16 16 16 16 8" />
        <circle cx="5.5" cy="18.5" r="2.5" />
        <circle cx="18.5" cy="18.5" r="2.5" />
    </svg>
);

const FastTruckIcon: React.FC = () => (
    <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M13 17h8l-2-6h-6v6z" />
        <path d="M1 17h2" />
        <path d="M5 17h8v-6H5z" />
        <circle cx="17" cy="17" r="2" />
        <circle cx="9" cy="17" r="2" />
        <path d="M1 11h4" />
        <path d="M1 14h3" />
    </svg>
);

const CheckCircleIcon: React.FC = () => (
    <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
        <polyline points="22 4 12 14.01 9 11.01" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
);

const BoxIcon: React.FC = () => (
    <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" />
        <polyline points="3.27 6.96 12 12.01 20.73 6.96" />
        <line x1="12" y1="22.08" x2="12" y2="12" />
    </svg>
);

const getAvailabilityColor = (availability?: string): { bg: string; text: string; dot: string } => {
    if (!availability) return { bg: "bg-gray-500/10", text: "text-gray-500", dot: "bg-gray-500" };

    const lower = availability.toLowerCase();
    if (lower.includes("in stock")) {
        return { bg: "bg-emerald-500/10", text: "text-emerald-600 dark:text-emerald-400", dot: "bg-emerald-500" };
    }
    if (lower.includes("only") || lower.includes("few")) {
        return { bg: "bg-amber-500/10", text: "text-amber-600 dark:text-amber-400", dot: "bg-amber-500" };
    }
    if (lower.includes("out") || lower.includes("unavailable")) {
        return { bg: "bg-red-500/10", text: "text-red-600 dark:text-red-400", dot: "bg-red-500" };
    }
    return { bg: "bg-sky-500/10", text: "text-sky-600 dark:text-sky-400", dot: "bg-sky-500" };
};

export const DeliveryInfo: React.FC<DeliveryInfoProps> = ({
    delivery,
    availability,
    stockQuantity
}) => {
    if (!delivery || delivery.length === 0) return null;

    const availabilityColors = getAvailabilityColor(availability);

    return (
        <div className="p-6 bg-surface border border-default rounded-2xl">
            <h4 className="text-lg font-semibold text-default mb-4 flex items-center gap-2">
                <span className="text-indigo-500"><TruckIcon /></span>
                Delivery & Availability
            </h4>

            {/* Availability badge */}
            {availability && (
                <div className={`inline-flex items-center gap-2 px-3 py-1.5 ${availabilityColors.bg} rounded-full mb-4`}>
                    <span className={`w-2 h-2 rounded-full ${availabilityColors.dot} animate-pulse`} />
                    <span className={`text-sm font-medium ${availabilityColors.text}`}>
                        {availability}
                    </span>
                    {stockQuantity && stockQuantity > 0 && stockQuantity <= 10 && (
                        <span className="text-xs text-secondary">
                            ({stockQuantity} left)
                        </span>
                    )}
                </div>
            )}

            {/* Delivery options */}
            <div className="space-y-3">
                {delivery.map((option, index) => (
                    <div
                        key={index}
                        className={`flex items-start gap-3 p-4 rounded-xl border transition-colors ${option.type === "fast"
                                ? "bg-gradient-to-r from-amber-500/5 to-orange-500/5 border-amber-500/20"
                                : "bg-surface-elevated border-transparent"
                            }`}
                    >
                        <div className={`shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${option.type === "fast"
                                ? "bg-gradient-to-br from-amber-400 to-orange-500 text-white"
                                : "bg-indigo-500/10 text-indigo-500"
                            }`}>
                            {option.type === "fast" ? <FastTruckIcon /> : <TruckIcon />}
                        </div>
                        <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 mb-1">
                                {option.type === "fast" && (
                                    <span className="px-2 py-0.5 bg-amber-500 text-white text-xs font-bold rounded">
                                        FASTEST
                                    </span>
                                )}
                                {option.type === "standard" && option.text.toLowerCase().includes("free") && (
                                    <span className="px-2 py-0.5 bg-emerald-500 text-white text-xs font-bold rounded">
                                        FREE
                                    </span>
                                )}
                            </div>
                            <p className="text-sm text-default leading-relaxed">
                                {option.text}
                            </p>
                            {option.date && (
                                <p className="text-xs text-secondary mt-1 flex items-center gap-1">
                                    <CheckCircleIcon />
                                    Arrives: {option.date}
                                </p>
                            )}
                        </div>
                    </div>
                ))}
            </div>

            {/* Stock indicator */}
            {stockQuantity && stockQuantity > 0 && (
                <div className="mt-4 pt-4 border-t border-default">
                    <div className="flex items-center gap-2 text-sm text-secondary">
                        <BoxIcon />
                        <span>
                            {stockQuantity > 10
                                ? "In stock - ships soon"
                                : `Only ${stockQuantity} left in stock`
                            }
                        </span>
                    </div>
                </div>
            )}
        </div>
    );
};