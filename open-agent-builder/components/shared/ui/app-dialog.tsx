"use client";

import React from "react";
import { motion } from "framer-motion";
import CurvyRect from "@/components/shared/layout/curvy-rect";
import { cn } from "@/utils/cn";
import {
  Dialog,
  DialogTrigger,
  DialogPortal,
  DialogOverlay,
  DialogClose,
  DialogHeader,
  DialogFooter,
  DialogTitle,
  DialogDescription,
  DialogContent as ShadDialogContent,
} from "@/components/ui/shadcn/dialog";

type AppDialogContentProps = React.ComponentPropsWithoutRef<
  typeof ShadDialogContent
> & {
  withCurvyRect?: boolean;
  bodyClassName?: string;
};

export function AppDialogContent({
  className,
  children,
  withCurvyRect = true,
  bodyClassName,
  ...props
}: AppDialogContentProps) {
  return (
    <ShadDialogContent
      className={cn(
        "sm:rounded-16 p-0 border border-border-faint bg-white relative overflow-hidden",
        className,
      )}
      {...props}
    >
      {withCurvyRect && (
        <CurvyRect className="absolute inset-0 pointer-events-none" allSides />
      )}
      <motion.div
        initial={{ opacity: 0, scale: 0.985, y: 24 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        transition={{ type: "spring", stiffness: 300, damping: 24, mass: 0.9 }}
        className={cn("relative p-16 pb-12", bodyClassName)}
      >
        {children}
      </motion.div>
    </ShadDialogContent>
  );
}

export {
  Dialog,
  DialogTrigger,
  DialogPortal,
  DialogOverlay,
  DialogClose,
  DialogHeader,
  DialogFooter,
  DialogTitle,
  DialogDescription,
};
