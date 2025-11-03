"use client";

import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/utils/cn";

interface TextRevealProps {
  text: string;
  isVisible: boolean;
  className?: string;
  delay?: number;
  duration?: number;
}

export function TextReveal({
  text,
  isVisible,
  className,
  delay = 0,
  duration = 0.3,
}: TextRevealProps) {
  return (
    <AnimatePresence>
      {isVisible && (
        <motion.span
          initial={{
            opacity: 0,
          }}
          animate={{
            opacity: 1,
          }}
          exit={{
            opacity: 0,
          }}
          transition={{
            duration,
            delay,
            ease: "easeInOut",
          }}
          className={cn("inline-block", className)}
        >
          {text}
        </motion.span>
      )}
    </AnimatePresence>
  );
}
