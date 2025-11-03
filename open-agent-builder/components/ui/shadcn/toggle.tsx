import { motion } from "motion/react";
import { useState } from "react";

import { cn } from "@/utils/cn";

export default function Toggle({
  checked,
  onChange,
  disabled,
}: {
  checked: boolean;
  onChange?: (checked: boolean) => void;
  disabled?: boolean;
}) {
  const [isHovering, setIsHovering] = useState(false);

  return (
    <button
      className={cn(
        "transition-all relative rounded-full group",
        checked ? "bg-heat-100" : "bg-black-alpha-10",
      )}
      style={{
        width: "50px",
        height: "20px",
        boxShadow: checked
          ? "0px 6px 12px 0px rgba(174, 37, 0, 0.12) inset, 0px 0.75px 0.75px 0px rgba(174, 37, 0, 0.06) inset, 0px 0.25px 0.25px 0px rgba(174, 37, 0, 0.06) inset"
          : "0px 6px 12px 0px rgba(0, 0, 0, 0.02) inset, 0px 0.75px 0.75px 0px rgba(0, 0, 0, 0.02) inset, 0px 0.25px 0.25px 0px rgba(0, 0, 0, 0.04) inset",
      }}
      type="button"
      onClick={() => onChange?.(!checked)}
      onMouseEnter={() => setIsHovering(true)}
      onMouseLeave={() => setIsHovering(false)}
      disabled={disabled}
    >
      <div
        className={cn(
          "overlay bg-[#FA4500] transition-opacity",
          checked
            ? "opacity-0 group-hover:opacity-100"
            : "opacity-0 group-hover:opacity-0",
        )}
        style={{
          background: "color(display-p3 0.9059 0.3294 0.0784)",
        }}
      />

      <motion.div
        animate={{
          x: checked ? 18 : 0,
        }}
        className="top-[2px] left-[2px] transition-[box-shadow] absolute rounded-full bg-accent-white"
        initial={{
          x: checked ? 18 : 0,
        }}
        style={{
          width: "28px",
          height: "16px",
          boxShadow: (() => {
            if (checked) {
              if (isHovering) {
                return "0px 6px 12px -3px rgba(174, 36, 0, 0.30), 0px 3px 6px -1px rgba(174, 37, 0, 0.12), 0px 1px 2px 0px rgba(174, 37, 0, 0.12), 0px 0.5px 0.5px 0px rgba(174, 37, 0, 0.24)";
              }

              return "0px 6px 12px -3px rgba(174, 36, 0, 0.30), 0px 3px 6px -1px rgba(174, 37, 0, 0.12), 0px 1px 2px 0px rgba(174, 37, 0, 0.12), 0px 0.5px 0.5px 0px rgba(174, 37, 0, 0.24)";
            }

            if (isHovering) {
              return "0px 6px 12px -3px rgba(0, 0, 0, 0.06), 0px 3px 6px -1px rgba(0, 0, 0, 0.06), 0px 1px 2px 0px rgba(0, 0, 0, 0.04), 0px 0.5px 0.5px 0px rgba(0, 0, 0, 0.08)";
            }

            return "0px 6px 12px -3px rgba(0, 0, 0, 0.06), 0px 3px 6px -1px rgba(0, 0, 0, 0.06), 0px 1px 2px 0px rgba(0, 0, 0, 0.04), 0px 0.5px 0.5px 0px rgba(0, 0, 0, 0.08)";
          })(),
        }}
      />
    </button>
  );
}
