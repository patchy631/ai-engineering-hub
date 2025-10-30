"use client";

import { useEffect, useState } from "react";
import { cn } from "@/utils/cn";

const asciiPatterns = [
  `·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·
  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  
·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·
  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  
·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·`,
  `·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·
  ·  ·  ·  ·  ▪  ·  ·  ·  ·  ·  ·  ·  ·  ▪  ·  ·  ·  ·  ·  
·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·
  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  
·  ·  ·  ·  ▪  ·  ·  ·  ·  ·  ·  ·  ·  ▪  ·  ·  ·  ·  ·  ·`,
  `·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·
  ·  ·  ·  ▪  ▄  ▪  ·  ·  ·  ·  ·  ·  ▪  ▄  ▪  ·  ·  ·  ·  
·  ·  ·  ·  ▪  ·  ·  ·  ·  ·  ·  ·  ·  ▪  ·  ·  ·  ·  ·  ·
  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  
·  ·  ·  ▪  ▄  ▪  ·  ·  ·  ·  ·  ·  ▪  ▄  ▪  ·  ·  ·  ·  ·`,
  `·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·
  ·  ·  ▪  ▄  █  ▄  ▪  ·  ·  ·  ·  ▪  ▄  █  ▄  ▪  ·  ·  ·  
·  ·  ·  ▪  ▄  ▪  ·  ·  ·  ·  ·  ·  ▪  ▄  ▪  ·  ·  ·  ·  ·
  ·  ·  ·  ▪  ·  ·  ·  ·  ·  ·  ·  ·  ·  ▪  ·  ·  ·  ·  ·  
·  ·  ▪  ▄  █  ▄  ▪  ·  ·  ·  ·  ▪  ▄  █  ▄  ▪  ·  ·  ·  ·`,
];

interface AsciiBackgroundProps {
  className?: string;
  variant?: "dots" | "grid" | "flame";
}

export function AsciiBackground({
  className,
  variant = "dots",
}: AsciiBackgroundProps) {
  const [frameIndex, setFrameIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setFrameIndex((prev) => (prev + 1) % asciiPatterns.length);
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div
      className={cn(
        "absolute inset-0 pointer-events-none select-none overflow-hidden",
        className,
      )}
    >
      <pre className="text-heat-100/3 font-mono text-[10px] leading-tight whitespace-pre absolute top-0 left-0 w-full h-full flex items-center justify-center">
        {asciiPatterns[frameIndex]}
      </pre>
    </div>
  );
}
