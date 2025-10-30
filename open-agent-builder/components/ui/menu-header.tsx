"use client";

import React from "react";
import { X } from "lucide-react";
import { cn } from "@/utils/cn";

interface MenuHeaderProps {
  title: string;
  onClose?: () => void;
  className?: string;
}

export function MenuHeader({ title, onClose, className }: MenuHeaderProps) {
  return (
    <div
      className={cn(
        "p-12 border-b border-border-faint flex items-center justify-between",
        className,
      )}
    >
      <h2 className="text-label-medium text-black-alpha-56">{title}</h2>
      {onClose && (
        <button
          onClick={onClose}
          className={cn(
            "w-24 h-24 flex items-center justify-center rounded-6 transition-all",
            "text-black-alpha-40 hover:text-black-alpha-56",
            "hover:bg-black-alpha-4",
            "active:scale-[0.98]",
          )}
        >
          <X className="w-12 h-12" />
        </button>
      )}
    </div>
  );
}
