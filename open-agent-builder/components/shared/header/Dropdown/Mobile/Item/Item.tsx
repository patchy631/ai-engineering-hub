"use client";
import { AnimatePresence, cubicBezier, motion } from "motion/react";
import { useState } from "react";

import {
  ConnectorToLeft,
  ConnectorToRight,
} from "@/components/shared/layout/curvy-rect";
import { NAV_ITEMS } from "@/components/shared/header/Nav/Nav";
import { cn } from "@/utils/cn";

export default function HeaderDropdownMobileItem({
  item,
}: {
  item: (typeof NAV_ITEMS)[number];
}) {
  const [open, setOpen] = useState(false);

  return (
    <>
      <a
        className="p-24 flex group relative"
        href={item.href}
        onClick={() => {
          setOpen((v) => !v);
        }}
      >
        <div className="h-1 bottom-0 absolute left-0 w-full bg-border-faint" />
        <ConnectorToRight className="-top-11 left-0" />
        <ConnectorToRight className="-bottom-10 left-0" />
        <ConnectorToLeft className="-top-11 right-0" />
        <ConnectorToLeft className="-bottom-10 right-0" />

        <span className="px-4 flex-1 text-label-medium text-accent-black">
          {item.label}
        </span>

        {item.dropdown && (
          <svg
            className={cn(
              "transition-all duration-200",
              open ? "rotate-180 text-accent-black" : "text-black-alpha-48",
            )}
            fill="none"
            height="24"
            viewBox="0 0 24 24"
            width="24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M8.4001 10.2L12.0001 13.8L15.6001 10.2"
              stroke="currentColor"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="1.25"
            />
          </svg>
        )}
      </a>

      <AnimatePresence>
        {open && (
          <motion.div
            animate={{ height: "auto", opacity: 1, filter: "blur(0px)" }}
            className="overflow-hidden"
            exit={{ height: 0, opacity: 0, filter: "blur(4px)" }}
            initial={{ height: 0, opacity: 0, filter: "blur(4px)" }}
            transition={{ duration: 0.3, ease: cubicBezier(0.4, 0, 0.2, 1) }}
          >
            {item.dropdown}

            <div className="h-44 relative">
              <ConnectorToRight className="-top-11 left-0" />
              <ConnectorToRight className="-bottom-10 left-0" />
              <ConnectorToLeft className="-top-11 right-0" />
              <ConnectorToLeft className="-bottom-10 right-0" />
              <div className="h-1 bottom-0 absolute left-0 w-full bg-border-faint" />
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
