import { ButtonHTMLAttributes, forwardRef } from "react";

import { cn } from "@/utils/cn";

import "./button.css";

interface Props extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary";
  size?: "default" | "large";
  disabled?: boolean;
  loadingLabel?: string;
  isLoading?: boolean;
}

const Button = forwardRef<HTMLButtonElement, Props>(
  (
    {
      variant = "secondary",
      size = "large",
      disabled,
      isLoading = false,
      loadingLabel = "Loading…",
      ...attrs
    },
    ref,
  ) => {
    const isNonInteractive = Boolean(disabled || isLoading);

    // Focus ring adapts to light/dark variants
    const focusRing =
      variant === "primary"
        ? "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-white"
        : "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-black";

    return (
      <button
        {...attrs}
        ref={ref}
        type={attrs.type ?? "button"}
        aria-disabled={isNonInteractive || undefined}
        aria-busy={isLoading || undefined}
        aria-live={isLoading ? "polite" : undefined}
        data-state={
          isLoading ? "loading" : isNonInteractive ? "disabled" : "idle"
        }
        className={cn(
          attrs.className,
          "flex items-center justify-center button relative [&>*]:relative",
          "text-label-medium lg-max:[&_svg]:size-24",
          `button-${variant} group/button`,
          focusRing,

          // Shared non-interactive styles
          "disabled:cursor-not-allowed",
          isNonInteractive && "cursor-not-allowed",

          // Size - default to large as shown in the example
          size === "default" && "rounded-8 px-10 py-6 gap-4",
          size === "large" && "rounded-10 px-12 py-8 gap-6",

          // Primary variant (orange/heat)
          variant === "primary" && [
            "text-accent-white",
            // Hover/active only when interactive
            !isNonInteractive &&
              "hover:bg-[color:var(--heat-90)] active:[scale:0.995]",
            // Disabled: dim a bit, no hover, dim overlay bg layer if present
            "disabled:opacity-80",
            "disabled:[&_.button-background]:opacity-70",
          ],

          // Secondary variant (grey)
          variant === "secondary" && [
            "text-accent-black",
            !isNonInteractive && "active:[scale:0.99] active:bg-black-alpha-7",
            "bg-black-alpha-4",
            !isNonInteractive && "hover:bg-black-alpha-6",
            // Disabled: lighter fill + muted text, no hover
            "disabled:bg-black-alpha-3",
            "disabled:text-black-alpha-48",
            "disabled:hover:bg-black-alpha-3",
          ],
        )}
        disabled={isNonInteractive}
      >
        {variant === "primary" && (
          <div className="overlay button-background !absolute" />
        )}

        {/* loading state (spinner) */}
        {isLoading && (
          <div
            className={cn(
              "w-16 h-16 border-2 rounded-full animate-spin",
              variant === "primary"
                ? "border-white/30 border-t-white"
                : "border-black/30 border-t-black",
            )}
            aria-hidden
          />
        )}

        {/* Screen reader-only loading label */}
        {isLoading && <span className="sr-only">{loadingLabel}</span>}

        {attrs.children}
      </button>
    );
  },
);

Button.displayName = "Button";

export default Button;
