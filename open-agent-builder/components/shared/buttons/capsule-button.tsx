"use client";

import React from "react";
import { cn } from "@/utils/cn";
import { LucideIcon } from "lucide-react";
import { AnimatePresence, motion } from "motion/react";
import AnimatedWidth from "@/components/shared/layout/animated-width";

interface CapsuleButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  icon?: LucideIcon | React.ComponentType<{ className?: string }>;
  iconPosition?: "left" | "right";
  children: React.ReactNode;
  size?: "sm" | "md" | "lg";
  fullWidth?: boolean;
  variant?: "primary" | "secondary" | "tertiary" | "ghost";
  loading?: boolean;
}

export function CapsuleButton({
  icon: Icon,
  iconPosition = "left",
  children,
  className,
  size = "md",
  fullWidth = false,
  variant = "primary",
  loading = false,
  disabled,
  ...props
}: CapsuleButtonProps) {
  const [isPressed, setIsPressed] = React.useState(false);

  const sizeClasses = {
    sm: "h-32 px-16 text-label-small gap-6",
    md: "h-40 px-20 text-label-medium gap-8",
    lg: "h-40 px-20 text-label-medium gap-8",
  };

  const iconSizes = {
    sm: "w-14 h-14",
    md: "w-16 h-16",
    lg: "w-16 h-16",
  };

  const variants = {
    primary: [
      "bg-heat-100 text-white",
      "hover:bg-heat-200",
      "active:scale-[0.98]",
      "shadow-[0_1px_2px_rgba(0,0,0,0.05)]",
      "hover:shadow-[0_4px_12px_rgba(250,93,25,0.25)]",
    ],
    secondary: [
      "bg-black text-white",
      "hover:bg-black/90",
      "active:scale-[0.98]",
      "shadow-[0_1px_2px_rgba(0,0,0,0.05)]",
      "hover:shadow-[0_4px_12px_rgba(0,0,0,0.15)]",
    ],
    tertiary: [
      "bg-white text-black border border-black-alpha-8",
      "hover:bg-black-alpha-4 hover:border-black-alpha-12",
      "active:scale-[0.98]",
    ],
    ghost: [
      "bg-transparent text-black-alpha-60",
      "hover:text-black hover:bg-black-alpha-4",
      "active:scale-[0.98]",
    ],
  };

  const isDisabled = disabled || loading;

  return (
    <button
      className={cn(
        // Base styles
        "inline-flex items-center justify-center rounded-full  transition-all duration-200",
        // Size
        sizeClasses[size],
        // Variant
        variants[variant],
        // Full width
        fullWidth && "w-full",
        // Disabled state
        isDisabled && [
          "opacity-50 cursor-not-allowed",
          "hover:shadow-none hover:bg-current",
        ],
        // Pressed state
        isPressed && "scale-[0.98]",
        className,
      )}
      disabled={isDisabled}
      onMouseDown={() => !isDisabled && setIsPressed(true)}
      onMouseUp={() => setIsPressed(false)}
      onMouseLeave={() => setIsPressed(false)}
      {...props}
    >
      <AnimatedWidth initial={{ width: "auto" }}>
        <AnimatePresence initial={false} mode="popLayout">
          {loading ? (
            <motion.div
              key="loading"
              animate={{ opacity: 1, filter: "blur(0px)", scale: 1 }}
              className="flex gap-8 items-center justify-center"
              exit={{ opacity: 0, filter: "blur(2px)", scale: 0.9 }}
              initial={{ opacity: 0, filter: "blur(2px)", scale: 0.95 }}
            >
              <span>Loading...</span>
            </motion.div>
          ) : (
            <motion.div
              key="content"
              animate={{ opacity: 1, filter: "blur(0px)", scale: 1 }}
              className="flex gap-8 items-center justify-center"
              exit={{ opacity: 0, filter: "blur(2px)", scale: 0.9 }}
              initial={{ opacity: 0, filter: "blur(2px)", scale: 0.95 }}
            >
              {Icon && iconPosition === "left" && (
                <span
                  className={cn(
                    iconSizes[size],
                    "flex-shrink-0 inline-flex items-center justify-center",
                  )}
                >
                  <Icon className="w-full h-full" />
                </span>
              )}
              <span>{children}</span>
              {Icon && iconPosition === "right" && (
                <span
                  className={cn(
                    iconSizes[size],
                    "flex-shrink-0 inline-flex items-center justify-center",
                  )}
                >
                  <Icon className="w-full h-full" />
                </span>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </AnimatedWidth>
    </button>
  );
}
