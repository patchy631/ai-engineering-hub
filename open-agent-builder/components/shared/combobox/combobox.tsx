import { animate, AnimatePresence, cubicBezier, motion } from "motion/react";
import { useEffect, useMemo, useRef, useState } from "react";

import { cn } from "@/utils/cn";
import { lockBody } from "../lockBody";
import PortalToBody from "../utils/portal-to-body";

export default function Combobox({
  placeholder,
  options,
  value,
  onChange,
  className,
}: {
  placeholder?: string;
  options: { label: string; value: string }[];
  value: string;
  onChange: (value: string) => void;
  className?: string;
}) {
  const selected = useMemo(() => {
    return options.find((option) => option.value === value);
  }, [options, value]);
  const [isOpen, setIsOpen] = useState(false);
  const [bounds, setBounds] = useState<DOMRect | null>(null);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    lockBody("combobox", isOpen);
  }, [isOpen]);

  useEffect(() => {
    document.addEventListener("click", (e) => {
      if (ref.current && e.composedPath().includes(ref.current)) {
        return;
      }

      setIsOpen(false);
    });
  }, []);

  return (
    <div className={cn("w-full", className)} ref={ref}>
      <button
        className={cn(
          "relative bg-accent-white flex w-full gap-4 rounded-8 p-6 pl-10",
          "before:inside-border before:border-black-alpha-8 hover:before:border-black-alpha-12 hover:bg-black-alpha-2",
          "text-body-medium",
          isOpen &&
            "!bg-accent-white before:!border-heat-100 before:!border-[1.25px]",
        )}
        type="button"
        onClick={(e) => {
          e.preventDefault();
          setIsOpen(!isOpen);
          setBounds(ref.current?.getBoundingClientRect() ?? null);
        }}
      >
        <div className={cn("flex-1", !selected && "text-black-alpha-40")}>
          {selected?.label || placeholder}
        </div>

        <motion.svg
          animate={{ rotate: isOpen ? 180 : 0 }}
          fill="none"
          height="20"
          viewBox="0 0 20 20"
          width="20"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M7 8.5L10 11.5L13 8.5"
            stroke="#262626"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeOpacity="0.56"
            strokeWidth="1.25"
          />
        </motion.svg>
      </button>

      <PortalToBody>
        <AnimatePresence initial={false}>
          {isOpen && bounds && (
            <motion.div
              animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
              className="fixed bg-accent-white rounded-12 z-[401]"
              exit={{ opacity: 0, y: 0, filter: "blur(4px)" }}
              initial={{ opacity: 0, y: -12, filter: "blur(4px)" }}
              style={{
                top: bounds.top + bounds.height + 8,
                left: bounds.left,
                width: bounds.width,
                boxShadow:
                  "0px 32px 40px 6px rgba(0, 0, 0, 0.02), 0px 12px 32px 0px rgba(0, 0, 0, 0.02), 0px 24px 32px -8px rgba(0, 0, 0, 0.02), 0px 8px 16px -2px rgba(0, 0, 0, 0.02), 0px 0px 0px 1px rgba(0, 0, 0, 0.04)",
              }}
              transition={{ duration: 0.2 }}
            >
              <div className="p-4">
                <Items
                  options={options}
                  onChange={(value) => {
                    onChange(value);
                    setIsOpen(false);
                  }}
                />
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </PortalToBody>
    </div>
  );
}

const Items = ({
  options,
  onChange,
}: {
  options: { label: string; value: string }[];
  onChange: (value: string) => void;
}) => {
  const backgroundRef = useRef<HTMLDivElement>(null);

  return (
    <div className="relative">
      <div
        className="absolute top-0 opacity-0 left-0 bg-black-alpha-4 rounded-8 w-full h-32 pointer-events-none"
        ref={backgroundRef}
      />

      {options.map((option) => (
        <button
          className="w-full group py-6 px-10 text-label-small"
          key={option.value}
          type="button"
          onClick={() => {
            onChange(option.value);
          }}
          onMouseEnter={(e) => {
            const t = e.target as HTMLElement;

            let target =
              t instanceof HTMLButtonElement
                ? t
                : (t.closest("button") as HTMLButtonElement);
            target = target.closest(".group") as HTMLButtonElement;

            animate(backgroundRef.current!, { scale: 0.995 }).then(() =>
              animate(backgroundRef.current!, { scale: 1 }),
            );

            animate(
              backgroundRef.current!,
              {
                y: target.offsetTop,
                opacity: 1,
              },
              {
                ease: cubicBezier(0.165, 0.84, 0.44, 1),
                duration: 0.2,
              },
            );
          }}
          onMouseLeave={() => {
            animate(backgroundRef.current!, { opacity: 0 });
          }}
        >
          {option.label}
        </button>
      ))}
    </div>
  );
};
