import { ArrowUpRight } from "lucide-react";
import { cn } from "@/utils/cn";

export interface NavItemRowProps {
  icon: React.ReactNode;
  label: string;
  description: string;
  href: string;
  target?: string;
  iconClassName?: string;
  className?: string;
}

export function NavItemRow({
  icon,
  label,
  description,
  href,
  target,
  iconClassName,
  className,
}: NavItemRowProps) {
  return (
    <a
      className={cn(
        "flex items-start gap-16 py-16 pl-24 lg-max:[&_svg]:size-24 lg:pl-44 group border-x hover:bg-black-alpha-2 border-b border-border-faint transition-all hover:text-heat-100",
        className,
      )}
      href={href}
      target={target}
    >
      <div className={iconClassName}>{icon}</div>

      <div className="min-w-0 flex-1">
        <div className="text-label-medium">{label}</div>

        <div className="text-body-medium mt-4 text-black-alpha-64 lg-max:hidden">
          {description}
        </div>
      </div>
    </a>
  );
}

export interface NavItemRowBigProps extends Omit<NavItemRowProps, "target"> {
  ctas?: { label: string; href: string; target?: string }[];
}

export function NavItemRowBig({
  icon,
  label,
  description,
  href,
  iconClassName,
  ctas,
}: NavItemRowBigProps) {
  return (
    <div className="flex items-start gap-16 py-22 pl-24 lg-max:[&_svg]:size-24 lg:pl-44 group border-x border-b transition-colors border-border-faint">
      <div className={iconClassName}>{icon}</div>

      <div className="min-w-0 flex-1">
        <a
          href={href}
          className="text-label-medium inline-block hover:text-heat-100 transition-colors"
        >
          {label}
        </a>

        <div className="text-body-medium mt-4 text-black-alpha-64 lg-max:hidden">
          {description}
        </div>

        {ctas && ctas.length > 0 && (
          <div className="mt-12 flex items-center gap-8 lg-max:hidden">
            {ctas.map((cta) => (
              <a
                key={cta.label}
                href={cta.href}
                target={cta.target}
                className="inline-flex items-center gap-6 px-12 py-6 rounded-6 text-label-small text-heat-100 bg-heat-4 hover:bg-heat-8 transition-colors whitespace-nowrap shrink-0"
              >
                <span>{cta.label}</span>
                <ArrowUpRight className="size-14" aria-hidden="true" />
              </a>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
