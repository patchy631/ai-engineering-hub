"use client";

import React from "react";
import { cn } from "@/utils/cn";
import { LucideIcon } from "lucide-react";

interface SlateButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  icon?:
    | LucideIcon
    | React.ComponentType<{
        className?: string;
        isHovered?: boolean;
        isOpen?: boolean;
      }>
    | React.ReactNode;
  iconPosition?: "left" | "right";
  children: React.ReactNode;
  size?: "sm" | "md" | "lg";
  fullWidth?: boolean;
  isLoading?: boolean;
  isOpen?: boolean;
}

export const SlateButton = React.forwardRef<
  HTMLButtonElement,
  SlateButtonProps
>(
  (
    {
      icon: Icon,
      iconPosition = "left",
      children,
      className,
      size = "md",
      fullWidth = false,
      isLoading = false,
      isOpen = false,
      disabled,
      ...props
    },
    ref,
  ) => {
    const [isHovered, setIsHovered] = React.useState(false);

    const sizeClasses = {
      sm: "h-32 px-12 text-body-small gap-6",
      md: "h-40 px-16 text-body-medium gap-8",
      lg: "h-48 px-24 text-body-large gap-10",
    };

    const iconSizes = {
      sm: "w-14 h-14",
      md: "w-16 h-16",
      lg: "w-20 h-20",
    };

    return (
      <button
        ref={ref}
        className={cn(
          // Base styles
          "inline-flex items-center justify-center rounded-12  transition-all",
          // Colors
          "bg-black-alpha-4 text-accent-black",
          "hover:bg-black-alpha-6",
          "active:scale-[0.98]",
          // Border
          // "border-0",
          // Size
          sizeClasses[size],
          // States
          disabled && "opacity-50 cursor-not-allowed",
          isLoading && "cursor-wait",
          // Full width
          fullWidth && "w-full",
          className,
        )}
        disabled={disabled || isLoading}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        {...props}
      >
        {isLoading ? (
          <div className={cn("animate-spin rounded-full", iconSizes[size])} />
        ) : (
          <>
            {Icon &&
              iconPosition === "left" &&
              (React.isValidElement(Icon) ? (
                Icon
              ) : (
                //@ts-ignore
                <Icon
                  className={cn(iconSizes[size], "flex-shrink-0")}
                  // @ts-ignore - Some icons support isHovered and isOpen
                  isHovered={isHovered}
                  isOpen={isOpen}
                />
              ))}
            {children}
            {Icon &&
              iconPosition === "right" &&
              (React.isValidElement(Icon) ? (
                Icon
              ) : (
                //@ts-ignore
                <Icon
                  className={cn(iconSizes[size], "flex-shrink-0")}
                  // @ts-ignore - Some icons support isHovered and isOpen
                  isHovered={isHovered}
                  isOpen={isOpen}
                />
              ))}
          </>
        )}
      </button>
    );
  },
);

SlateButton.displayName = "SlateButton";
