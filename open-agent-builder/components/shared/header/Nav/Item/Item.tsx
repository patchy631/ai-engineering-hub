"use client";

import { JSX } from "react";

import { useHeaderContext } from "@/components/shared/header/HeaderContext";
import { cn } from "@/utils/cn";

import ChevronDown from "./_svg/ChevronDown";

export default function HeaderNavItem({
  label,
  href,
  dropdown,
}: {
  label: string;
  href: string;
  dropdown?: JSX.Element;
}) {
  const { dropdownContent, setDropdownContent, clearDropdown } =
    useHeaderContext();

  const active = dropdownContent === dropdown;

  return (
    <a
      className="p-6 relative flex h-32 group rounded-8 active:scale-[0.98] transition-all duration-[50ms] active:duration-[100ms]"
      href={href}
      onMouseEnter={() => {
        if (dropdown) {
          setDropdownContent(dropdown);
        } else {
          clearDropdown(true);
        }
      }}
      onMouseLeave={() => {
        if (!dropdown) return;

        clearDropdown();
      }}
    >
      <span
        className={cn(
          "overlay pointer-events-none group-hover:bg-black-alpha-4 transition-all scale-95 group-active:duration-[100ms] duration-[150ms] group-hover:scale-100 group-active:bg-black-alpha-7",
          active && "!scale-100 !bg-black-alpha-4",
        )}
      />

      <span className="px-4 text-label-medium text-accent-black">{label}</span>

      {dropdown && <ChevronDown />}
    </a>
  );
}
