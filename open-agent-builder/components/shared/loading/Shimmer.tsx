"use client";

import { cn } from "@/utils/cn";
import { useState, useEffect } from "react";
import ScrambleText from "@/components/ui/motion/scramble-text";

export const Shimmer = ({
  className,
  text = "Loading...",
}: {
  className?: string;
  text?: string;
}) => {
  const [isInView, setIsInView] = useState(false);

  useEffect(() => {
    setIsInView(true);
  }, []);

  return (
    <div className={cn("w-full", className)}>
      {text && (
        <div className="mb-4 text-label-large text-black-alpha-56">
          <ScrambleText
            text={text}
            delay={0}
            duration={1.2}
            isInView={isInView}
          />
        </div>
      )}
      <div className="space-y-3">
        <div className="h-4 rounded-8 bg-gradient-to-r from-black-alpha-4 via-black-alpha-8 to-black-alpha-4 animate-shimmer mb-2 w-3/4">
          <span className="sr-only">{text}</span>
        </div>
        <div className="h-4 rounded-8 bg-gradient-to-r from-black-alpha-4 via-black-alpha-8 to-black-alpha-4 animate-shimmer animation-delay-150 mb-2 w-1/2"></div>
        <div className="h-4 rounded-8 bg-gradient-to-r from-black-alpha-4 via-black-alpha-8 to-black-alpha-4 animate-shimmer animation-delay-300 mb-2 w-full"></div>
        <div className="h-4 rounded-8 bg-gradient-to-r from-black-alpha-4 via-black-alpha-8 to-black-alpha-4 animate-shimmer animation-delay-450 mb-2 w-1/2"></div>
      </div>
    </div>
  );
};

export const ShimmerSingle = ({
  className,
  text,
}: {
  className?: string;
  text?: string;
}) => {
  const [isInView, setIsInView] = useState(false);

  useEffect(() => {
    setIsInView(true);
  }, []);

  return (
    <div className={cn("w-full", className)}>
      {text && (
        <div className="mb-2 text-label-small text-black-alpha-56">
          <ScrambleText
            text={text}
            delay={0}
            duration={1}
            isInView={isInView}
          />
        </div>
      )}
      <div className="h-4 rounded-8 bg-gradient-to-r from-black-alpha-4 via-black-alpha-8 to-black-alpha-4 animate-shimmer w-full"></div>
    </div>
  );
};

// Chart shimmer with fire glow effect
export const ChartShimmer = ({
  className,
  text = "Loading chart data...",
}: {
  className?: string;
  text?: string;
}) => {
  const [isInView, setIsInView] = useState(false);

  useEffect(() => {
    setIsInView(true);
  }, []);

  return (
    <div className={cn("w-full h-full relative overflow-hidden", className)}>
      {/* Subtle fire glow background */}
      <div className="absolute inset-0 bg-gradient-to-br from-heat-4/10 via-transparent to-heat-4/10 animate-pulse" />

      {/* Loading text */}
      {text && (
        <div className="absolute top-4 left-4 text-label-small text-black-alpha-56 z-10">
          <ScrambleText
            text={text}
            delay={0}
            duration={0.8}
            isInView={isInView}
          />
        </div>
      )}

      {/* Chart bars */}
      <div className="absolute bottom-0 left-0 right-0 flex items-end justify-between px-4 pb-4 gap-2">
        {Array.from({ length: 8 }, (_, i) => (
          <div
            key={i}
            className="flex-1 bg-gradient-to-t from-black-alpha-8 to-transparent rounded-t-4 animate-shimmer"
            style={{
              height: `${Math.random() * 60 + 20}%`,
              animationDelay: `${i * 100}ms`,
            }}
          />
        ))}
      </div>
    </div>
  );
};
