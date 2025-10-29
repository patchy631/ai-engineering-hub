"use client";

import { AnimatePresence, motion } from "motion/react";
import { nanoid } from "nanoid";
import { useEffect, useRef, useState } from "react";

import PortalToBody from "@/components/shared/utils/portal-to-body";
import { cn } from "@/utils/cn";

export default function Tooltip({
  delay = 0.5,
  offset = 8,
  wrapperClassName,
  className,
  ...props
}: {
  description?: string;
  children?: React.ReactNode;
  offset?: number;
  delay?: number;
  wrapperClassName?: string;
  className?: string;
}) {
  const [hovering, setHovering] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  const [bounds, setBounds] = useState<{
    x: number;
    y: number;
    width: number;
    height: number;
  } | null>(null);

  useEffect(() => {
    if (ref.current) {
      const element = ref.current;
      const parent = element.parentElement!;

      const onMouseEnter = () => {
        setBounds(parent.getBoundingClientRect());
        setHovering(true);
      };
      const onMouseLeave = () => setHovering(false);

      if (!parent) return;

      parent.addEventListener("mouseenter", onMouseEnter);
      parent.addEventListener("mouseleave", onMouseLeave);

      return () => {
        parent.removeEventListener("mouseenter", onMouseEnter);
        parent.removeEventListener("mouseleave", onMouseLeave);
      };
    }
  }, []);

  if (!props.description) return props.children;

  return (
    <div className="contents" ref={ref}>
      <PortalToBody>
        <AnimatePresence initial={false} mode="popLayout">
          {hovering && (
            <div
              className={cn(
                "fixed pointer-events-none flex-center z-[121]",
                wrapperClassName,
              )}
              style={{
                left: bounds?.x,
                top: bounds?.y,
                width: bounds?.width,
                height: bounds?.height,
              }}
            >
              <motion.div
                animate={{
                  y: 0,
                  opacity: 1,
                  filter: "blur(0px)",
                  transition: {
                    type: "spring",
                    stiffness: 240,
                    damping: 16,
                    filter: { duration: 0.4 },
                    delay,
                  },
                }}
                className={cn(
                  "py-10 px-16 rounded-12 max-w-248 absolute w-max text-body-medium text-accent-white bg-black-alpha-64 backdrop-blur-[6px] z-[121]",
                  className,
                )}
                dangerouslySetInnerHTML={{ __html: props.description }}
                exit={{
                  y: -8,
                  opacity: 0,
                  filter: "blur(4px)",
                  transition: { type: "spring", stiffness: 300, damping: 16 },
                }}
                initial={{ y: 8, opacity: 0, filter: "blur(4px)" }}
                key={nanoid()}
                style={{
                  boxShadow:
                    "0px 16px 24px -8px rgba(0, 0, 0, 0.06), 0px 8px 16px -4px rgba(0, 0, 0, 0.06)",
                  bottom: `calc(100% - ${offset}px)`,
                }}
                transition={{
                  type: "spring",
                  stiffness: 160,
                  damping: 13,
                  filter: { duration: 0.4 },
                }}
              />
            </div>
          )}
        </AnimatePresence>
      </PortalToBody>
    </div>
  );
}
