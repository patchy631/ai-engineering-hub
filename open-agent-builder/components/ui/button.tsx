import { ButtonHTMLAttributes, forwardRef, ReactNode } from "react";
import { cn } from "@/utils/cn";

/**
 * Unified Button Component
 *
 * Only two variants:
 * - primary: Orange/heat color for primary actions
 * - secondary: Grey for secondary actions
 *
 * @example
 * // Primary button (orange)
 * <Button variant="primary">Save Changes</Button>
 *
 * // Secondary button (grey) - default
 * <Button>Cancel</Button>
 *
 * // With icon
 * <Button variant="primary">
 *   <UploadIcon className="w-16 h-16" />
 *   <span>Upload</span>
 * </Button>
 */

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary";
  size?: "default" | "large";
  isLoading?: boolean;
  loadingLabel?: string;
  children: ReactNode;
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      variant = "secondary",
      size = "large",
      isLoading = false,
      loadingLabel = "Loading…",
      disabled,
      className,
      children,
      ...props
    },
    ref
  ) => {
    const isNonInteractive = Boolean(disabled || isLoading);

    return (
      <button
        ref={ref}
        type={props.type ?? "button"}
        disabled={isNonInteractive}
        aria-disabled={isNonInteractive || undefined}
        aria-busy={isLoading || undefined}
        aria-live={isLoading ? "polite" : undefined}
        data-state={
          isLoading ? "loading" : isNonInteractive ? "disabled" : "idle"
        }
        className={cn(
          // Base styles
          "flex items-center justify-center relative",
          "text-label-medium font-medium",
          "transition-all duration-200",
          "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2",

          // Size variants
          size === "default" && "rounded-8 px-10 py-6 gap-4 text-13",
          size === "large" && "rounded-10 px-12 py-8 gap-6 text-14",

          // Primary variant (orange/heat)
          variant === "primary" && [
            "bg-heat-100 text-white",
            "shadow-[0px_-6px_12px_0px_rgba(255,0,0,0.2)_inset,0px_2px_4px_0px_rgba(255,77,0,0.12)]",
            !isNonInteractive && [
              "hover:bg-heat-90",
              "hover:shadow-[0px_-6px_12px_0px_rgba(255,0,0,0.2)_inset,0px_4px_8px_0px_rgba(255,77,0,0.16)]",
              "active:scale-[0.995]",
            ],
            "disabled:opacity-80 disabled:cursor-not-allowed",
            "focus-visible:ring-white",
          ],

          // Secondary variant (grey)
          variant === "secondary" && [
            "bg-black-alpha-4 text-accent-black",
            !isNonInteractive && [
              "hover:bg-black-alpha-6",
              "active:scale-[0.99] active:bg-black-alpha-7",
            ],
            "disabled:bg-black-alpha-3 disabled:text-black-alpha-48 disabled:cursor-not-allowed",
            "focus-visible:ring-black",
          ],

          // Custom className
          className
        )}
        {...props}
      >
        {/* Primary variant gradient overlay */}
        {variant === "primary" && (
          <div className="absolute inset-0 rounded-inherit bg-gradient-to-b from-white/6 to-transparent pointer-events-none" />
        )}

        {/* Loading spinner */}
        {isLoading && (
          <div
            className={cn(
              "w-16 h-16 border-2 rounded-full animate-spin",
              variant === "primary"
                ? "border-white/30 border-t-white"
                : "border-black/30 border-t-black"
            )}
            aria-hidden
          />
        )}

        {/* Screen reader loading label */}
        {isLoading && <span className="sr-only">{loadingLabel}</span>}

        {/* Button content */}
        <div className="relative flex items-center gap-inherit">
          {children}
        </div>
      </button>
    );
  }
);

Button.displayName = "Button";

export default Button;
export { Button, type ButtonProps };