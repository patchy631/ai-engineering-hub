import { HTMLAttributes } from "react";

import Badge from "@/components/ui/shadcn/badge";
import CurvyRect from "@/components/shared/layout/curvy-rect";
import { cn } from "@/utils/cn";

type SectionHeadProps = {
  children: React.ReactNode;
  title: string | React.ReactNode;
  titleClassName?: string;
  titleShadow?: boolean;
  badgeContent?: React.ReactNode;
  badgeClassName?: string;
  description?: React.ReactNode | string;
  descriptionClassName?: string;
  containerClassName?: string;
  action?: React.ReactNode;
  smallerHeader?: boolean;
};

export default function SectionHead({
  children,
  title,
  titleClassName,
  titleShadow = true,
  badgeContent,
  badgeClassName,
  description,
  descriptionClassName,
  containerClassName,
  action,
  smallerHeader = false,
  ...attrs
}: SectionHeadProps &
  Omit<HTMLAttributes<HTMLDivElement>, keyof SectionHeadProps>) {
  return (
    <div
      {...attrs}
      className={cn(
        smallerHeader
          ? "relative py-64 lg:py-88 overflow-clip z-[1]"
          : "relative py-88 lg:py-143 overflow-clip z-[1]",
        attrs.className,
      )}
    >
      <CurvyRect allSides />
      <div className="h-1 bg-border-faint bottom-0 left-0 w-full absolute" />

      <div className={cn("relative", containerClassName)}>
        {badgeContent && (
          <Badge className={cn("mx-auto px-12 pt-16", badgeClassName)}>
            {badgeContent}
          </Badge>
        )}

        <div>
          <h2
            className={cn(
              "lg:w-max relative mx-auto text-accent-black text-title-h2 pb-8 pt-12 px-20 text-center section-head-title",
              titleClassName,
            )}
          >
            {titleShadow && (
              <div
                className="overlay -z-[1] p-[inherit] section-head-shadow"
                aria-hidden
              >
                {title}
              </div>
            )}

            {title}
          </h2>

          {description && (
            <div
              className={cn(
                "section-head-title max-w-369 px-20 py-8 relative w-full mx-auto !text-black-alpha-72 text-body-large text-center mb-32 last:mb-0",
                descriptionClassName,
              )}
            >
              {description}

              <div
                className="overlay -z-[1] p-[inherit] section-head-shadow"
                aria-hidden
              >
                {description}
              </div>
            </div>
          )}

          {action}
        </div>
      </div>

      {children}
    </div>
  );
}
