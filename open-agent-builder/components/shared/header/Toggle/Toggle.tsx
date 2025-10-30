"use client";

import Button from "@/components/ui/shadcn/button";
import { useHeaderContext } from "@/components/shared/header/HeaderContext";
import { cn } from "@/utils/cn";

export default function HeaderToggle({
  dropdownContent,
}: {
  dropdownContent: React.ReactNode;
}) {
  const {
    dropdownContent: headerDropdownContent,
    clearDropdown,
    setDropdownContent,
  } = useHeaderContext();

  return (
    <Button
      className="lg:hidden"
      variant="secondary"
      onClick={() => {
        if (dropdownContent === headerDropdownContent) {
          clearDropdown(true);
        } else {
          setDropdownContent(dropdownContent);
        }
      }}
    >
      <svg
        className="!size-20"
        fill="none"
        height="20"
        viewBox="0 0 20 20"
        width="20"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          className={cn("transition-all origin-center", {
            "rotate-45 -translate-y-4": headerDropdownContent,
          })}
          d="M2.28906 13.9609H17.7057"
          stroke="#262626"
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth="1.25"
          style={{
            transformBox: "fill-box",
          }}
        />
        <path
          className={cn("transition-all origin-center", {
            "-rotate-45 translate-y-3 translate-x-[2.5px]":
              headerDropdownContent,
          })}
          d="M2.28906 6.03906H17.7057"
          stroke="#262626"
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth="1.25"
        />
      </svg>
    </Button>
  );
}
