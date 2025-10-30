"use client";

import React, { useEffect, useRef, useState } from "react";

import CurvyRect from "@/components/shared/layout/curvy-rect";
import { cn } from "@/utils/cn";

interface FlameButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode;
  className?: string;
  variant?: "primary" | "secondary";
}

// Flame patterns for hover effect - designed to tile and fill the button
const flamePatterns = [
  `▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲
▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲
 ▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲ 
  ▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲  
   ▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲   `,
  ` ▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲ 
▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲
▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲
 ▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲ 
  ▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲  `,
  `▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲
 ▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲ 
  ▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲  
   ▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲   
▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲`,
];

export function FlameButton({
  children,
  className,
  variant = "primary",
  onMouseDown,
  onMouseUp,
  onMouseLeave,
  ...props
}: FlameButtonProps) {
  const [flameIndex, setFlameIndex] = useState(0);
  const [isHovered, setIsHovered] = useState(false);
  const [isPressed, setIsPressed] = useState(false);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (isHovered || isPressed) {
      const speed = isPressed ? 80 : 150; // Faster when pressed
      intervalRef.current = setInterval(() => {
        setFlameIndex((prev) => (prev + 1) % flamePatterns.length);
      }, speed);
    } else {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [isHovered, isPressed]);

  const handleMouseDown = (e: React.MouseEvent<HTMLButtonElement>) => {
    setIsPressed(true);
    onMouseDown?.(e);
  };

  const handleMouseUp = (e: React.MouseEvent<HTMLButtonElement>) => {
    setIsPressed(false);
    onMouseUp?.(e);
  };

  const handleMouseLeave = (e: React.MouseEvent<HTMLButtonElement>) => {
    setIsPressed(false);
    setIsHovered(false);
    onMouseLeave?.(e);
  };

  return (
    <button
      className={cn(
        "relative overflow-hidden rounded-8 transition-all  text-body-medium",
        "bg-white border border-heat-100 text-heat-100",
        "hover:border-heat-200 hover:shadow-[0_0_20px_rgba(250,93,25,0.2)]",
        "active:shadow-[0_0_30px_rgba(250,93,25,0.4)]",
        className,
      )}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={handleMouseLeave}
      onMouseDown={handleMouseDown}
      onMouseUp={handleMouseUp}
      {...props}
    >
      <CurvyRect className="absolute inset-0 pointer-events-none" allSides />

      {/* Animated flame background on hover/click */}
      {(isHovered || isPressed) && (
        <div className="absolute inset-0 pointer-events-none select-none overflow-hidden">
          <div
            className={cn(
              "absolute inset-0 flex items-center justify-center transition-opacity duration-200",
              isPressed ? "opacity-25" : "opacity-10",
            )}
          >
            <div
              className="text-heat-100 font-mono leading-none w-full h-full"
              style={{
                fontSize: "3px",
                lineHeight: "3px",
                whiteSpace: "pre",
                overflow: "hidden",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                transform: isPressed ? "scale(1.1)" : "scale(1)",
                transition: "transform 0.1s ease",
                textShadow: isPressed
                  ? "0 0 3px rgba(250,93,25,0.8)"
                  : "0 0 1px rgba(250,93,25,0.5)",
              }}
            >
              {flamePatterns[flameIndex]}
            </div>
          </div>
        </div>
      )}

      <span className="relative z-10 flex items-center justify-center">
        {children}
      </span>
    </button>
  );
}
