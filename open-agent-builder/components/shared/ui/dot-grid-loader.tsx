"use client";

import { motion } from "motion/react";
import React from "react";

interface DotGridLoaderProps {
  size?: number; // pixel size of each dot
  cols?: number;
  rows?: number;
  className?: string;
  animated?: boolean;
  intensityMap?: number[]; // per-dot base opacity 0..1, length cols*rows
}

export function DotGridLoader({
  size = 10,
  cols = 3,
  rows = 3,
  className,
  animated = true,
  intensityMap,
}: DotGridLoaderProps) {
  const total = cols * rows;
  const defaultMap = Array.from({ length: total }).map((_, i) => {
    // Row alphas tuned to hero prompt style: top=0.4, middle=1, bottom=0.12
    const row = Math.floor(i / cols);
    if (row === 0) return 0.4; // top
    if (row === 1) return 1.0; // middle
    return 0.12; // bottom
  });
  const bases =
    intensityMap && intensityMap.length === total ? intensityMap : defaultMap;
  return (
    <div
      className={className}
      style={{
        display: "grid",
        gridTemplateColumns: `repeat(${cols}, ${size}px)`,
        gap: Math.max(2, Math.round(size / 3)),
      }}
    >
      {Array.from({ length: total }).map((_, i) => {
        const base = bases[i] ?? 0.8;
        return (
          <motion.div
            key={i}
            initial={{ opacity: base }}
            animate={
              animated ? { opacity: [base, 1, base] } : { opacity: base }
            }
            transition={
              animated
                ? { duration: 1.1, repeat: Infinity, delay: i * 0.08 }
                : undefined
            }
            style={{ width: size, height: size }}
            className="rounded-[2px] bg-heat-100"
          />
        );
      })}
    </div>
  );
}

export default DotGridLoader;
