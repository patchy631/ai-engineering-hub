"use client";

import React, { useEffect, useRef } from "react";
import { cn } from "@/utils/cn";
import { setIntervalOnVisible } from "@/utils/set-timeout-on-visible";
import data from "@/components/shared/effects/flame/explosion-data.json";

interface AsciiFlameBackgroundProps {
  className?: string;
  colorClassName?: string;
  fontSizePx?: number;
  lineHeightPx?: number;
}

// Reusable ASCII flame background (same frames used by CoreReliableBarFlame)
export default function AsciiFlameBackground({
  className,
  colorClassName = "text-heat-100/30",
  fontSizePx = 10,
  lineHeightPx = 12.5,
}: AsciiFlameBackgroundProps) {
  const wrapperRef = useRef<HTMLDivElement>(null);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let index = 0;
    const stop = setIntervalOnVisible({
      element: wrapperRef.current,
      callback: () => {
        index += 1;
        if (index >= (data as string[]).length) index = 0;
        if (ref.current) ref.current.innerHTML = (data as string[])[index];
      },
      interval: 80,
    });

    return () => stop?.();
  }, []);

  return (
    <div
      ref={wrapperRef}
      className={cn("relative pointer-events-none select-none", className)}
    >
      <div
        ref={ref}
        className={cn(
          "font-ascii absolute inset-0 fc-decoration",
          colorClassName,
        )}
        style={{
          whiteSpace: "pre",
          fontSize: `${fontSizePx}px`,
          lineHeight: `${lineHeightPx}px`,
        }}
      />
    </div>
  );
}
