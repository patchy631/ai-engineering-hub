"use client";

import React from "react";
import { AnimatedDotIcon } from "@/components/shared/animated-dot-icon";

interface AsciiDotLoaderProps {
  size?: number;
  animated?: boolean;
  className?: string;
  pattern?: Parameters<typeof AnimatedDotIcon>[0]["pattern"];
}

// Thin wrapper to reuse the exact ASCII pixel effect used on the home hero
export default function AsciiDotLoader({
  size = 20,
  animated = true,
  className,
  pattern = "logs",
}: AsciiDotLoaderProps) {
  return (
    <AnimatedDotIcon
      size={size}
      active={animated}
      alwaysHeat
      className={className}
      pattern={pattern}
    />
  );
}
