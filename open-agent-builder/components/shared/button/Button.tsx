import { Children, ButtonHTMLAttributes } from "react";

import { cn } from "@/utils/cn";

interface Props extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "tertiary" | "playground" | "destructive";
  size?: "default" | "large";
  disabled?: boolean;
}

export default function Button({
  variant = "primary",
  size = "default",
  disabled,
  ...attrs
}: Props) {
  const children = handleChildren(attrs.children);

  return (
    <button
      {...attrs}
      type={attrs.type ?? "button"}
      className={cn(
        attrs.className,
        "[&>span]:px-6 flex items-center justify-center button relative [&>*]:relative",
        "text-label-medium lg-max:[&_svg]:size-24",
        `button-${variant} group/button`,
        {
          "rounded-8 p-6": size === "default",
          "rounded-10 p-8 gap-2": size === "large",

          "text-accent-white active:[scale:0.995]": variant === "primary",
          "text-accent-black active:[scale:0.99] active:bg-black-alpha-7": [
            "secondary",
            "tertiary",
            "playground",
          ].includes(variant),
          "bg-black-alpha-4 hover:bg-black-alpha-6": variant === "secondary",
          "hover:bg-black-alpha-4": variant === "tertiary",
        },
        variant === "playground" && [
          "before:inside-border before:border-black-alpha-4",
          disabled
            ? "before:opacity-0 bg-black-alpha-4 text-black-alpha-24"
            : "hover:bg-black-alpha-4 hover:before:opacity-0 active:before:opacity-0",
        ],
      )}
      disabled={disabled}
    >
      {variant === "primary" && (
        <div className="overlay button-background !absolute" />
      )}

      {children}
    </button>
  );
}

const handleChildren = (children: React.ReactNode) => {
  return Children.toArray(children).map((child) => {
    if (typeof child === "string") {
      return <span key={child}>{child}</span>;
    }

    return child;
  });
};
