"use client";

import React, { useEffect, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X } from "lucide-react";
import { useAtom } from "jotai";
import { cn } from "@/utils/cn";
import { isMobileSheetOpenAtom } from "@/atoms/sheets";

interface MobileSheetProps {
  isOpen: boolean;
  onClose: () => void;
  title?: React.ReactNode;
  showCloseButton?: boolean;
  position?: "top" | "bottom";
  spacing?: "sm" | "md" | "lg"; // sm=16px, md=20px, lg=24px from all edges
  children: React.ReactNode;
  className?: string;
  contentHeight?: "auto" | "fill" | "full"; // 'auto' for small content, 'fill' for lists, 'full' for nearly fullscreen
  contentPadding?: boolean; // Whether to add default padding to content area (default: true)
  closeOnOverlayClick?: boolean; // Whether clicking the overlay should close the sheet (default: true)
}

// Hook to auto-close mobile sheets when transitioning to desktop
function useAutoCloseOnDesktop(isOpen: boolean, onClose: () => void) {
  useEffect(() => {
    if (!isOpen) return;

    const handleResize = () => {
      // Close immediately if screen becomes larger than mobile breakpoint (768px for lg:)
      if (window.innerWidth >= 1024) {
        onClose();
      }
    };

    window.addEventListener("resize", handleResize);

    // Check immediately in case we're already on desktop
    handleResize();

    return () => {
      window.removeEventListener("resize", handleResize);
    };
  }, [isOpen, onClose]);
}

export function MobileSheet({
  isOpen,
  onClose,
  title,
  showCloseButton = false,
  position = "bottom",
  spacing = "sm",
  children,
  className,
  contentHeight = "auto",
  contentPadding = true,
  closeOnOverlayClick = true,
}: MobileSheetProps) {
  const [, setIsMobileSheetOpen] = useAtom(isMobileSheetOpenAtom);
  const scrollRef = useRef<HTMLDivElement>(null);
  const [showTopGradient, setShowTopGradient] = useState(false);
  const [showBottomGradient, setShowBottomGradient] = useState(false);

  // Handle global mobile sheet state changes (always reflect actual open state)
  useEffect(() => {
    setIsMobileSheetOpen(isOpen);
    return () => setIsMobileSheetOpen(false);
  }, [isOpen, setIsMobileSheetOpen]);

  // Lock background scroll when sheet is open, restore when closed
  useEffect(() => {
    if (typeof document === "undefined") return;
    if (isOpen) {
      const previousOverflow = document.body.style.overflow;
      document.body.style.overflow = "hidden";
      return () => {
        document.body.style.overflow = previousOverflow;
      };
    } else {
      document.body.style.overflow = "";
    }
  }, [isOpen]);

  // Auto-close when transitioning to desktop
  useAutoCloseOnDesktop(isOpen, onClose);

  // Check initial scroll state when sheet opens
  useEffect(() => {
    if (isOpen && scrollRef.current) {
      // Small delay to ensure content is rendered
      setTimeout(() => {
        const target = scrollRef.current;
        if (target) {
          const isAtTop = target.scrollTop <= 5;
          const isAtBottom =
            target.scrollHeight - target.scrollTop - target.clientHeight <= 5;
          const hasScroll = target.scrollHeight > target.clientHeight;

          setShowTopGradient(hasScroll && !isAtTop);
          setShowBottomGradient(hasScroll && !isAtBottom);
        }
      }, 50);
    }
  }, [isOpen]);

  // Enhanced close handler
  const handleClose = () => {
    // Re-enable page scroll after closing sheet
    document.body.style.overflow = "";
    onClose();
  };

  // Define spacing values
  const getSpacingClass = () => {
    const horizontalSpacing =
      spacing === "sm"
        ? "left-16 right-16"
        : spacing === "md"
          ? "left-20 right-20"
          : "left-24 right-24";

    if (contentHeight === "full") {
      if (spacing === "sm") return `${horizontalSpacing} top-16 bottom-16`;
      if (spacing === "md") return `${horizontalSpacing} top-20 bottom-20`;
      return `${horizontalSpacing} top-24 bottom-24`;
    }

    const verticalSpacing =
      position === "top"
        ? spacing === "sm"
          ? "top-16"
          : spacing === "md"
            ? "top-20"
            : "top-24"
        : spacing === "sm"
          ? "bottom-16"
          : spacing === "md"
            ? "bottom-20"
            : "bottom-24";

    return `${horizontalSpacing} ${verticalSpacing}`;
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <div
          className="fixed inset-0 z-[120] lg:hidden"
          onClick={() => {
            if (closeOnOverlayClick) {
              handleClose();
            }
          }}
        >
          {/* Sheet content - positioned from top or bottom */}
          <motion.div
            initial={{
              opacity: 0,
              y: position === "top" ? -50 : 50,
            }}
            animate={{ opacity: 1, y: 0 }}
            exit={{
              opacity: 0,
              y: position === "top" ? -50 : 50,
            }}
            transition={{
              type: "spring",
              stiffness: 300,
              damping: 30,
              mass: 0.8,
            }}
            className={cn("absolute", getSpacingClass())}
            onClick={(e) => e.stopPropagation()}
          >
            <div
              className={cn(
                "bg-background-base border border-border-faint rounded-12 shadow-2xl overflow-hidden",
                className,
              )}
            >
              {/* Header */}
              {(title || showCloseButton) && (
                <div className="px-24 py-16 border-b border-border-faint flex items-center justify-between">
                  {title && (
                    <h2 className="text-label-large text-accent-black">
                      {title}
                    </h2>
                  )}
                  {showCloseButton && (
                    <button
                      onClick={handleClose}
                      className={cn(
                        "h-32 w-32 flex items-center justify-center transition-all rounded-6 border border-border-faint",
                        "bg-black-alpha-4 hover:bg-black-alpha-6 active:scale-[0.98]",
                        "text-black-alpha-64 hover:text-accent-black",
                      )}
                      aria-label="Close"
                    >
                      <X className="w-16 h-16" />
                    </button>
                  )}
                </div>
              )}

              {/* Content with gradient overlays */}
              <div className="relative group">
                <div
                  ref={scrollRef}
                  className={cn(
                    contentHeight === "full"
                      ? "h-full"
                      : contentHeight === "fill"
                        ? "h-[65vh]"
                        : "max-h-[60vh]",
                    "overflow-y-auto scrollbar-hide",
                    contentPadding && "p-16",
                  )}
                  onScroll={(e) => {
                    const target = e.currentTarget;
                    const isAtTop = target.scrollTop <= 5;
                    const isAtBottom =
                      target.scrollHeight -
                        target.scrollTop -
                        target.clientHeight <=
                      5;
                    const hasScroll = target.scrollHeight > target.clientHeight;

                    // Update gradient visibility states
                    setShowTopGradient(hasScroll && !isAtTop);
                    setShowBottomGradient(hasScroll && !isAtBottom);
                  }}
                >
                  {children}
                </div>

                {/* Animated fade gradients */}
                <motion.div
                  className="absolute top-0 left-0 right-0 h-24 bg-gradient-to-b from-white to-transparent pointer-events-none z-10"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: showTopGradient ? 1 : 0 }}
                  transition={{ duration: 0.2, ease: "easeInOut" }}
                />
                <motion.div
                  className="absolute bottom-0 left-0 right-0 h-24 bg-gradient-to-t from-white to-transparent pointer-events-none z-10"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: showBottomGradient ? 1 : 0 }}
                  transition={{ duration: 0.2, ease: "easeInOut" }}
                />
              </div>
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}
