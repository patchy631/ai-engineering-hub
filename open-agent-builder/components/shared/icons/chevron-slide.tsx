"use client";

import React from "react";
import { cn } from "@/utils/cn";

type Direction = "left" | "right";

interface ChevronSlideProps extends React.SVGAttributes<SVGElement> {
  direction?: Direction;
  size?: number; // pixel size for width/height
}

export function ChevronSlide({
  direction = "right",
  size = 16,
  className,
  ...props
}: ChevronSlideProps) {
  const translateClass =
    direction === "right"
      ? "group-hover:translate-x-8"
      : "group-hover:-translate-x-8";
  const orientationClass = direction === "right" ? "" : "rotate-180";

  return (
    <svg
      className={cn(
        "transition-all",
        translateClass,
        orientationClass,
        className,
      )}
      fill="none"
      height={size}
      width={size}
      viewBox="0 0 20 20"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
      {...props}
    >
      <path
        d="M8.5 13L11.5 10L8.5 7"
        stroke="currentColor"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth="1.25"
      />
    </svg>
  );
}

export default ChevronSlide;
