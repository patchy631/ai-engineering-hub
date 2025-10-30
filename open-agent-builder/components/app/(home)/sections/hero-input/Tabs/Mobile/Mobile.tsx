//@ts-nocheck
import { animate, AnimatePresence, cubicBezier, motion } from "motion/react";
import { useEffect, useRef, useState } from "react";

import { tabs } from "@/components/app/(home)/sections/hero-input/Tabs/Tabs";
import { cn } from "@/utils/cn";
import { Endpoint } from "@/components/shared/Playground/Context/types";

export default function HeroInputTabsMobile(props: {
  setTab: (tab: Endpoint) => void;
  tab: Endpoint;
  allowedModes?: Endpoint[];
}) {
  // Filter tabs based on allowedModes if provided
  const visibleTabs = props.allowedModes
    ? tabs.filter((tab) => props.allowedModes.includes(tab.value))
    : tabs;

  const activeTab = visibleTabs.find((tab) => tab.value === props.tab)!;
  const [isOpen, setIsOpen] = useState(false);

  const ref = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (window.innerWidth > 996) {
      return;
    }

    document.addEventListener("click", (e) => {
      if (ref.current && e.composedPath().includes(ref.current)) {
        return;
      }

      setIsOpen(false);
    });
  }, []);

  return (
    <>
      <button
        className="py-8 px-10 flex items-center rounded-10 before:inside-border before:border-black-alpha-4 relative lg:hidden gap-4"
        ref={ref}
        onClick={() => setIsOpen(!isOpen)}
      >
        <activeTab.icon size={24} alwaysHeat />
        <div className="px-6 text-label-medium">{activeTab.label}</div>
        <svg
          className={cn(
            "transition-all duration-200",
            isOpen ? "rotate-180 text-accent-black" : "text-black-alpha-48",
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
      </button>

      <AnimatePresence mode="popLayout">
        {isOpen && (
          <motion.div
            animate={{ opacity: 1, filter: "blur(0px)" }}
            className="absolute z-[1001] top-[calc(100%-4px)] left-[calc(50%-(50vw-6px))] w-[calc(100vw-12px)]"
            exit={{ opacity: 0, filter: "blur(2px)" }}
            initial={{ opacity: 0, filter: "blur(2px)" }}
            transition={{
              duration: 0.2,
              ease: cubicBezier(0.25, 0.1, 0.25, 1.0),
            }}
          >
            <div
              className="mx-auto w-full p-4 max-w-366 rounded-16 bg-accent-white"
              style={{
                boxShadow:
                  "0 32px 40px 6px rgba(0, 0, 0, 0.02), 0 12px 32px 0 rgba(0, 0, 0, 0.02), 0 24px 32px -8px rgba(0, 0, 0, 0.02), 0 8px 16px -2px rgba(0, 0, 0, 0.02), 0 0 0 1px rgba(0, 0, 0, 0.04)",
              }}
            >
              <div className="py-10 px-12 text-label-small text-black-alpha-48">
                Output
              </div>

              <MenuItems
                setTab={props.setTab}
                tab={props.tab}
                visibleTabs={visibleTabs}
              />
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}

function MenuItems(props: {
  tab: Endpoint;
  setTab: (tab: Endpoint) => void;
  visibleTabs: typeof tabs;
}) {
  const backgroundRef = useRef<HTMLDivElement>(null);

  return (
    <div className="relative">
      <div
        className="absolute top-0 opacity-0 left-0 bg-black-alpha-4 rounded-12 w-full pointer-events-none"
        ref={backgroundRef}
      />

      {props.visibleTabs.map((tab) => (
        <div
          className="text-label-small select-none cursor-pointer flex gap-12 py-12 px-16"
          key={tab.value}
          onClick={() => {
            animate(
              backgroundRef.current!,
              {
                scaleX: [1, 0.99, 1],
                scaleY: [1, 0.96, 1],
                opacity: [1, 0.9, 1],
              },
              {
                ease: cubicBezier(0.165, 0.84, 0.44, 1),
                duration: 0.15,
              },
            );

            props.setTab(tab.value);
          }}
          onMouseEnter={async (e) => {
            const child = e.currentTarget as HTMLElement;

            if (backgroundRef.current?.getBoundingClientRect().height === 0) {
              backgroundRef.current!.style.height = child.offsetHeight + "px";
            }

            if (getComputedStyle(backgroundRef.current!).opacity === "0") {
              await animate(
                backgroundRef.current!,
                {
                  y: child.offsetTop,
                },
                {
                  ease: cubicBezier(0.165, 0.84, 0.44, 1),
                  duration: 0.01,
                },
              );
            }

            animate(backgroundRef.current!, { scale: 0.995 }).then(() =>
              animate(backgroundRef.current!, { scale: 1 }),
            );

            animate(
              backgroundRef.current!,
              {
                y: child.offsetTop,
                opacity: 1,
                height: child.offsetHeight + "px",
              },
              {
                ease: cubicBezier(0.165, 0.84, 0.44, 1),
                duration: 0.2,
              },
            );
          }}
          onMouseLeave={() => {
            animate(
              backgroundRef.current!,
              {
                opacity: 0,
              },
              {
                ease: cubicBezier(0.165, 0.84, 0.44, 1),
                duration: 0.2,
              },
            );
          }}
        >
          <div className="size-24 p-2">
            <tab.icon size={20} alwaysHeat />
          </div>
          <div className="px-6 text-label-medium">{tab.label}</div>
        </div>
      ))}
    </div>
  );
}
