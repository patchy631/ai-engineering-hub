import CurvyRect from "@/components/shared/layout/curvy-rect";
import { cn } from "@/utils/cn";
import { ArrowUpRight } from "lucide-react";

interface Props {
  navigationItems: {
    label: string;
    items: {
      icon: React.ReactNode;
      label: string;
      description: string;
      href: string;
      target?: string;
      big?: boolean;
      ctas?: { label: string; href: string; target?: string }[];
      sectionLabel?: string;
      iconClassName?: string;
    }[];
  }[];
  sideLabel: string;
  sideContent: React.ReactNode;
  sideItem: {
    icon: React.ReactNode;
    label: string;
    description: string;
    href: string;
    target?: string;
  };
}

export default function HeaderDropdownContent({
  navigationItems,
  sideLabel,
  sideContent,
  sideItem,
}: Props) {
  return (
    <div className="lg-max:max-w-[unset] container lg:flex gap-16">
      {navigationItems.map((item, index) => (
        <div className="flex-1" key={index}>
          <GroupLabel label={item.label} />

          {/* Default section (items without sectionLabel) */}
          <div
            className={cn(
              "grid gap-x-16",
              navigationItems.length === 1 && "lg:grid-cols-2",
            )}
          >
            {item.items
              .filter((it) => !it.sectionLabel && !it.big)
              .map((it) => (
                <Item item={it} key={it.label} />
              ))}
            {item.items
              .filter((it) => !it.sectionLabel && it.big)
              .map((it) => (
                <ItemBig item={it} key={it.label} />
              ))}
          </div>

          {/* Additional sections within the same column */}
          {Array.from(
            new Set(
              item.items
                .map((it) => it.sectionLabel)
                .filter(Boolean) as string[],
            ),
          ).map((section) => (
            <div key={section}>
              {/* <GroupLabel label={section} /> */}
              <div
                className={cn(
                  "grid gap-x-16",
                  navigationItems.length === 1 && "lg:grid-cols-2",
                )}
              >
                {item.items
                  .filter((it) => it.sectionLabel === section && !it.big)
                  .map((it) => (
                    <Item item={it} key={it.label} />
                  ))}
                {item.items
                  .filter((it) => it.sectionLabel === section && it.big)
                  .map((it) => (
                    <ItemBig item={it} key={it.label} />
                  ))}
              </div>
            </div>
          ))}

          <div className="h-42 border-t border-border-faint border-x -mt-1 relative lg-max:hidden">
            <CurvyRect
              className="-top-1 absolute -left-1 w-[calc(100%+2px)]"
              top
            />
            <CurvyRect
              className="bottom-full absolute -left-1 w-[calc(100%+2px)]"
              bottom
            />
          </div>
        </div>
      ))}

      <div className="flex-1 max-w-360 relative">
        <div className="h-full w-1 absolute top-0 left-0 bg-border-faint" />
        <GroupLabel label={sideLabel} />

        <div className="hidden lg:contents">{sideContent}</div>

        <Item item={sideItem} />

        <div className="h-42 border-t border-border-faint border-r -mt-1 relative lg-max:hidden">
          <CurvyRect
            className="-top-1 absolute left-0 w-[calc(100%+1px)]"
            top
          />
          <CurvyRect
            className="bottom-full absolute left-0 w-[calc(100%+1px)]"
            bottom
          />
        </div>
      </div>
    </div>
  );
}

const GroupLabel = ({ label }: { label: string }) => {
  return (
    <div className="text-body-medium py-16 lg:py-20 lg:border-x border-b border-border-faint px-24 lg:px-44 text-black-alpha-64">
      {label}
    </div>
  );
};

const Item = ({
  item,
}: {
  item: {
    icon: React.ReactNode;
    label: string;
    description: string;
    href: string;
    target?: string;
    iconClassName?: string;
  };
}) => {
  return (
    <a
      className="flex items-start gap-16 py-16 pl-24 lg-max:[&_svg]:size-24 lg:pl-44 group border-x hover:bg-black-alpha-2 border-b border-border-faint transition-all hover:text-heat-100"
      href={item.href}
      key={item.label}
      target={item.target}
    >
      <div className={item.iconClassName}>{item.icon}</div>

      <div className="min-w-0 flex-1">
        <div className="text-label-medium">{item.label}</div>

        <div className="text-body-medium mt-4 text-black-alpha-64 lg-max:hidden">
          {item.description}
        </div>
      </div>
    </a>
  );
};

const ItemBig = ({
  item,
}: {
  item: {
    icon: React.ReactNode;
    label: string;
    description: string;
    href: string;
    target?: string;
    ctas?: { label: string; href: string; target?: string }[];
    iconClassName?: string;
  };
}) => {
  return (
    <div
      className="flex items-start gap-16 py-22 pl-24 lg-max:[&_svg]:size-24 lg:pl-44 group border-x border-b transition-colors border-border-faint"
      key={item.label}
    >
      <div className={item.iconClassName}>{item.icon}</div>

      <div className="min-w-0 flex-1">
        <a
          href={item.href}
          target={item.target}
          className="text-label-medium inline-block hover:text-heat-100 transition-colors"
        >
          {item.label}
        </a>

        <div className="text-body-medium mt-4 text-black-alpha-64 lg-max:hidden">
          {item.description}
        </div>

        {item.ctas && item.ctas.length > 0 && (
          <div className="mt-12 flex items-center gap-8 lg-max:hidden">
            {item.ctas.map((cta) => (
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
};
