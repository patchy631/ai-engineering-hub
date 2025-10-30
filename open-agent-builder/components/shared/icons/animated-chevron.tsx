"use client";

import React from "react";
import { ChevronDown, ChevronUp } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/utils/cn";

interface AnimatedChevronProps {
  isOpen: boolean;
  className?: string;
  size?: "sm" | "md" | "lg";
}

export function AnimatedChevron({
  isOpen,
  className,
  size = "md",
}: AnimatedChevronProps) {
  const sizeClasses = {
    sm: "h-12 w-12",
    md: "h-16 w-16",
    lg: "h-20 w-20",
  };

  return (
    <div className={cn("flex items-center justify-center", sizeClasses[size])}>
      <AnimatePresence mode="wait" initial={false}>
        {isOpen ? (
          <motion.div
            key="chevron-up"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            <ChevronUp
              className={cn(
                sizeClasses[size],
                "text-black-alpha-40",
                className,
              )}
            />
          </motion.div>
        ) : (
          <motion.div
            key="chevron-down"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            <ChevronDown
              className={cn(
                sizeClasses[size],
                "text-black-alpha-40",
                className,
              )}
            />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
