import Link from "next/link";
import { cn } from "@/utils/cn";

interface FireActionLinkProps {
  href?: string;
  label: string;
  className?: string;
  variant?: "link" | "button";
  onClick?: () => void;
}

export function FireActionLink({
  href,
  label,
  className,
  variant = "link",
  onClick,
}: FireActionLinkProps) {
  const baseClasses =
    variant === "button"
      ? cn(
          "inline-block py-4 px-8 rounded-6",
          "text-label-small text-heat-100 bg-heat-4",
          "hover:bg-heat-8 transition-all",
          "active:scale-[0.98]",
          className,
        )
      : cn(
          "text-label-small text-secondary hover:text-heat-100 transition-all",
          "hover:underline underline-offset-4",
          "active:scale-[0.98]",
          className,
        );

  if (onClick) {
    return (
      <button onClick={onClick} className={baseClasses}>
        {label}
      </button>
    );
  }

  return (
    <Link href={href || "#"} className={baseClasses}>
      {label}
    </Link>
  );
}
