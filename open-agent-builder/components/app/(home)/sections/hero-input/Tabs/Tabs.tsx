import { animate } from "motion";
import { Fragment, useRef } from "react";

import EndpointsSearch from "@/components/app/(home)/sections/endpoints/EndpointsSearch/EndpointsSearch";
import EndpointsCrawl from "@/components/app/(home)/sections/endpoints/EndpointsCrawl/EndpointsCrawl";
import EndpointsMap from "@/components/app/(home)/sections/endpoints/EndpointsMap/EndpointsMap";
import EndpointsScrape from "@/components/app/(home)/sections/endpoints/EndpointsScrape/EndpointsScrape";
import EndpointsExtract from "@/components/app/(home)/sections/endpoints/EndpointsExtract/EndpointsExtract";

import { cn } from "@/utils/cn";
import Tooltip from "@/components/ui/shadcn/tooltip";
import { Endpoint } from "@/components/shared/Playground/Context/types";

export const tabs = [
  {
    label: "Scrape",
    value: Endpoint.Scrape,
    action: "scraping",
    description:
      "Scrapes only the specified URL without crawling subpages. Outputs the content from the page.",
    icon: EndpointsScrape,
  },
  {
    label: "Search",
    value: Endpoint.Search,
    description: "Search the web and get full content from results",
    action: "searching",
    icon: EndpointsSearch,
    new: true,
  },
  {
    label: "Map",
    value: Endpoint.Map,
    action: "mapping",
    description: "Attempts to output all website's urls in a few seconds.",
    icon: EndpointsMap,
  },
  {
    label: "Crawl",
    value: Endpoint.Crawl,
    action: "crawling",
    description:
      "Crawls a URL and all its accessible subpages, outputting the content from each page.",
    icon: EndpointsCrawl,
  },
  {
    label: "Extract",
    value: Endpoint.Extract,
    action: "extracting",
    description:
      "Extract structured data from pages using LLMs. Provide URLs and a schema to get organized data.",
    icon: EndpointsExtract,
    new: true,
  },
];

export default function HeroInputTabs(props: {
  setTab: (tab: Endpoint) => void;
  tab: Endpoint;
  disabled?: boolean;
  allowedModes?: Endpoint[];
}) {
  // Filter tabs based on allowedModes if provided
  const visibleTabs = props.allowedModes
    ? tabs.filter((tab) => props.allowedModes!.includes(tab.value))
    : tabs;

  const activeIndex = visibleTabs.findIndex((tab) => tab.value === props.tab);

  const backgroundRef = useRef<HTMLDivElement>(null);

  return (
    <div
      className="bg-black-alpha-4 flex items-center rounded-10 p-2 relative lg-max:hidden"
      style={{
        boxShadow:
          "0px 6px 12px 0px rgba(0, 0, 0, 0.02) inset, 0px 0.75px 0.75px 0px rgba(0, 0, 0, 0.02) inset, 0px 0.25px 0.25px 0px rgba(0, 0, 0, 0.04) inset",
      }}
    >
      <div
        className="absolute top-2 left-2 h-32 bg-accent-white rounded-8 w-89"
        ref={backgroundRef}
        style={{
          boxShadow:
            "0px 6px 12px -3px rgba(0, 0, 0, 0.04), 0px 3px 6px -1px rgba(0, 0, 0, 0.04), 0px 1px 2px 0px rgba(0, 0, 0, 0.04), 0px 0.5px 0.5px 0px rgba(0, 0, 0, 0.06)",
        }}
      />

      {visibleTabs.map((tab, index) => (
        <Fragment key={tab.value}>
          {index > 0 && (
            <div
              className={cn(
                "px-2 transition-all",
                !(index !== activeIndex && index !== activeIndex + 1) &&
                  "opacity-0",
              )}
            >
              <div className="w-1 h-12 bg-black-alpha-5" />
            </div>
          )}

          <button
            className={cn(
              "text-label-medium p-6 relative transition-all group flex items-center",
              tab.value === props.tab
                ? "text-accent-black"
                : "text-black-alpha-56",
              !tab.new && "pr-4",
            )}
            key={tab.value}
            ref={(element) => {
              if (element && backgroundRef.current) {
                if (activeIndex === index) {
                  animate(
                    backgroundRef.current,
                    {
                      x: element.offsetLeft - 2,
                      width: element.offsetWidth - 1,
                    },
                    {
                      type: "spring",
                      stiffness: 200,
                      damping: 23,
                    },
                  );
                }
              }
            }}
            onClick={(e) => {
              props.setTab(tab.value);

              const t = e.target as HTMLElement;

              const target =
                t instanceof HTMLButtonElement
                  ? t
                  : (t.closest("button") as HTMLButtonElement);

              if (backgroundRef.current) {
                animate(backgroundRef.current, { scale: 0.975 }).then(() =>
                  animate(backgroundRef.current!, { scale: 1 }),
                );

                animate(
                  backgroundRef.current,
                  {
                    x: target.offsetLeft - 2,
                    width: target.offsetWidth - 1,
                  },
                  {
                    type: "spring",
                    stiffness: 250,
                    damping: 25,
                  },
                );
              }
            }}
          >
            {tab.icon && <tab.icon active={tab.value === props.tab} />}

            <span className="px-6"> {tab.label}</span>

            {tab.new && (
              <div
                className={cn(
                  "py-2 px-6 rounded-4 text-[12px]/[16px] font-[450] transition-all",
                  tab.value === props.tab
                    ? "bg-heat-12 text-heat-100"
                    : "bg-black-alpha-4 text-black-alpha-56",
                )}
              >
                New
              </div>
            )}

            <Tooltip delay={0.25} description={tab.description} offset={-8} />
          </button>
        </Fragment>
      ))}
    </div>
  );
}
