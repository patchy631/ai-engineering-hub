"use client";

import React from "react";
import { cn } from "@/utils/cn";
import { TrendingUp, TrendingDown } from "lucide-react";

interface StatCardProps {
  label: string;
  value: string | number;
  change?: number; // Percentage change
  suffix?: string;
  prefix?: string;
  icon?: React.ReactNode;
  trend?: "up" | "down" | "neutral";
  className?: string;
}

export function StatCard({
  label,
  value,
  change,
  suffix,
  prefix,
  icon,
  trend,
  className,
}: StatCardProps) {
  const trendColor =
    trend === "up"
      ? "text-green-600"
      : trend === "down"
        ? "text-red-600"
        : "text-black-alpha-64";
  const trendBg =
    trend === "up"
      ? "bg-green-50"
      : trend === "down"
        ? "bg-red-50"
        : "bg-black-alpha-4";

  return (
    <div
      className={cn(
        "p-5 lg:p-6 border border-border-faint rounded-12 bg-white",
        "hover:border-black-alpha-16 transition-colors",
        className,
      )}
    >
      <div className="flex items-start justify-between mb-3">
        <p className="text-label-small text-black-alpha-64">{label}</p>
        {icon && <div className="w-5 h-5 text-black-alpha-40">{icon}</div>}
      </div>

      <div className="space-y-2">
        <div className="flex items-baseline gap-1">
          {prefix && (
            <span className="text-body-large text-black-alpha-64">
              {prefix}
            </span>
          )}
          <span className="text-h3 font-semibold text-accent-black">
            {value}
          </span>
          {suffix && (
            <span className="text-body-large text-black-alpha-64">
              {suffix}
            </span>
          )}
        </div>

        {(change !== undefined || trend) && (
          <div className="flex items-center gap-2">
            {trend && (
              <div
                className={cn(
                  "w-6 h-6 rounded-6 flex items-center justify-center",
                  trendBg,
                )}
              >
                {trend === "up" ? (
                  <TrendingUp className={cn("w-3.5 h-3.5", trendColor)} />
                ) : trend === "down" ? (
                  <TrendingDown className={cn("w-3.5 h-3.5", trendColor)} />
                ) : null}
              </div>
            )}
            {change !== undefined && (
              <span className={cn("text-body-small ", trendColor)}>
                {change > 0 && "+"}
                {change}%
              </span>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
