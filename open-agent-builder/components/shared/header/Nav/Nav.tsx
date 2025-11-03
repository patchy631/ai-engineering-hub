import EndpointsCrawl from "@/components/app/(home)/sections/endpoints/EndpointsCrawl/EndpointsCrawl";
import EndpointsScrape from "@/components/app/(home)/sections/endpoints/EndpointsScrape/EndpointsScrape";
import EndpointsSearch from "@/components/app/(home)/sections/endpoints/EndpointsSearch/EndpointsSearch";
import EndpointsExtract from "@/components/app/(home)/sections/endpoints/Extract/Extract";
import EndpointsMcp from "@/components/app/(home)/sections/endpoints/Mcp/Mcp";
import { RenderEndpointIcon } from "@/components/shared/header/Nav/RenderEndpointIcon";
import HeaderDropdownContent from "@/components/shared/header/Dropdown/Content/Content";
import HeaderDropdownGithub from "@/components/shared/header/Dropdown/Github/Github";
import HeaderDropdownStories from "@/components/shared/header/Dropdown/Stories/Stories";

import Affiliate from "./_svg/Affiliate";
import Api from "./_svg/Api";
import ArrowRight from "./_svg/ArrowRight";
import Careers from "./_svg/Careers";
import Changelog from "./_svg/Changelog";
import Chats from "./_svg/Chats";
import Lead from "./_svg/Lead";
import Platforms from "./_svg/Platforms";
import Research from "./_svg/Research";
import Student from "./_svg/Student";
import Templates from "./_svg/Templates";
import HeaderNavItem from "./Item/Item";
import MCPIcon from "./_svg/MCP";
import Image from "@/components/shared/image/Image";
import GithubFlame from "@/components/shared/header/Dropdown/Github/Flame/Flame";
import EndpointsMap from "@/components/app/(home)/sections/endpoints/EndpointsMap/EndpointsMap";

export default function HeaderNav() {
  return (
    <div className="flex gap-8 relative lg-max:hidden select-none">
      {NAV_ITEMS.map((item) => (
        <HeaderNavItem key={item.label} {...item} />
      ))}
    </div>
  );
}

export const NAV_ITEMS = [
  {
    label: "Products",
    href: "#",
    dropdown: (
      <HeaderDropdownContent
        navigationItems={[
          {
            label: "Endpoints",
            items: [
              {
                icon: (
                  <RenderEndpointIcon
                    icon={EndpointsScrape}
                    alwaysHeat
                    triggerOnHover
                  />
                ),
                label: "Scrape",
                description: "Turn any url into clean data",
                href: "https://docs.firecrawl.dev/features/scrape",
                iconClassName: "-mt-1",
              },
              {
                icon: (
                  <RenderEndpointIcon
                    icon={EndpointsCrawl}
                    alwaysHeat
                    triggerOnHover
                  />
                ),
                label: "Crawl",
                description: "Crawl entire websites",
                href: "https://docs.firecrawl.dev/features/crawl",
                iconClassName: "-mt-1",
              },
              {
                icon: (
                  <RenderEndpointIcon
                    icon={EndpointsSearch}
                    alwaysHeat
                    triggerOnHover
                  />
                ),
                label: "Search",
                description: "Search and get page content",
                href: "https://docs.firecrawl.dev/features/search",
                iconClassName: "-mt-1",
              },
              {
                icon: (
                  <RenderEndpointIcon
                    icon={EndpointsMap}
                    alwaysHeat
                    triggerOnHover
                  />
                ),
                label: "Map",
                description: "Get all links from a website",
                href: "https://docs.firecrawl.dev/features/map",
                iconClassName: "-mt-1",
              },
              {
                icon: (
                  <RenderEndpointIcon
                    icon={EndpointsMcp}
                    alwaysHeat
                    triggerOnHover
                  />
                ),
                label: "MCP",
                description: "Connect Firecrawl to agents",
                href: "https://docs.firecrawl.dev/features/mcp",
                iconClassName: "-mt-1",
              },

              // Extract section in the same column, highlighted as a separate product
              // {
              //   icon: <RenderEndpointIcon icon={EndpointsExtract} alwaysHeat triggerOnHover />,
              //   label: 'Extract',
              //   description: 'Get structured data from single pages or entire websites with AI.',
              //   href: '/extract',
              //   big: true,
              //   sectionLabel: 'Extract Product',
              //   iconClassName: 'mt-4',
              //   ctas: [
              //     { label: 'View Extract', href: '/extract' },
              //     { label: 'Try it now', href: '/playground?mode=extract' }
              //   ]
              // },
            ],
          },
          {
            label: "Use Cases",
            items: [
              {
                icon: <Chats />,
                label: "AI Platforms",
                description: "Let customers build AI apps",
                href: "https://docs.firecrawl.dev/use-cases/ai-platforms",
                target: "_blank",
              },
              {
                icon: <Lead />,
                label: "Lead Enrichment",
                description: "Enhance sales data",
                href: "https://docs.firecrawl.dev/use-cases/lead-enrichment",
                target: "_blank",
              },
              {
                icon: <Platforms />,
                label: "SEO Platforms",
                description: "Power SEO/GEO tools",
                href: "https://docs.firecrawl.dev/use-cases/seo-platforms",
                target: "_blank",
              },
              {
                icon: <Research />,
                label: "Deep Research",
                description: "Build research agents",
                href: "https://docs.firecrawl.dev/use-cases/deep-research",
                target: "_blank",
              },
              {
                icon: <ArrowRight />,
                label: "View more",
                description: "Explore all use cases",
                href: "https://docs.firecrawl.dev/use-cases/overview",
                target: "_blank",
              },
            ],
          },
        ]}
        sideContent={<HeaderDropdownStories />}
        sideItem={{
          icon: <ArrowRight />,
          label: "Customer stories",
          description: "Browse Firecrawl success stories",
          href: "/blog/category/customer-stories",
        }}
        sideLabel="Customer Stories"
      />
    ),
  },
  {
    label: "Playground",
    href: "/playground",
  },
  {
    label: "Docs",
    href: "https://docs.firecrawl.dev",
  },
  {
    label: "Pricing",
    href: "/pricing",
  },
  {
    label: "Blog",
    href: "/blog",
  },
  {
    label: "Extract",
    href: "#",
    dropdown: (
      <HeaderDropdownContent
        navigationItems={[
          {
            label: "Extract API",
            items: [
              // { icon: <Templates />, label: 'Templates', description: 'Jumpstart your web scraping', href: '/templates' },
              {
                icon: (
                  <RenderEndpointIcon
                    icon={EndpointsExtract}
                    alwaysHeat
                    triggerOnHover
                  />
                ),
                label: "Extract",
                description: "Get structured data from entire websites",
                href: "/extract",
              },
              {
                icon: (
                  <div className="text-heat-100">
                    <Platforms />
                  </div>
                ),
                label: "Playground",
                description: "Try it out in the /extract playground",
                href: "/app/extract-playground",
              },
              // { icon: <ArrowRight/>, label: 'Docs', description: 'Read the docs.', href: 'https://docs.firecrawl.dev/features/extract', target: '_blank' },
            ],
          },
        ]}
        sideContent={
          <div className="py-24 px-44 border-b border-border-faint relative overflow-clip">
            {/* <div className="size-40 relative mb-17"> */}
            {/*  */}
            {/* </div> */}

            <div className="text-label-large">
              Get web data with a prompt. <br />
              Collect structured data from any number of URLs or entire domains.
            </div>

            <GithubFlame />
          </div>
        }
        sideItem={{
          icon: <ArrowRight />,
          label: "See Docs",
          description: "Read the docs.",
          href: "https://docs.firecrawl.dev/features/extract",
        }}
        sideLabel="/extract"
      />
    ),
  },
  {
    label: "Resources",
    href: "#",
    dropdown: (
      <HeaderDropdownContent
        navigationItems={[
          {
            label: "Resources",
            items: [
              // { icon: <Templates />, label: 'Templates', description: 'Jumpstart your web scraping', href: '/templates' },
              {
                icon: <Changelog />,
                label: "Changelog",
                description: "Latest APl updates for Firecrawl",
                href: "/changelog",
              },
              {
                icon: <Api />,
                label: "API Status",
                description: "See maintenance, uptime and more",
                href: "https://firecrawl.betteruptime.dev/",
                target: "_blank",
              },
              {
                icon: <Careers />,
                label: "Careers",
                description: "Join our team, we're hiring!",
                href: "/careers",
              },
              {
                icon: <Affiliate />,
                label: "Creator & OSS Program",
                description: "Earn rewards for referring customers",
                href: "/creator-oss-program",
              },
              {
                icon: <Student />,
                label: "Student Program",
                description: "Get free credits for your projects",
                href: "/student-program",
              },
              {
                icon: <MCPIcon />,
                label: "MCP",
                description: "Connect Firecrawl to agents",
                href: "https://docs.firecrawl.dev/features/mcp",
              },
            ],
          },
        ]}
        sideContent={<HeaderDropdownGithub />}
        sideItem={{
          icon: <ArrowRight />,
          label: "See Github",
          description: "View the repository",
          href: "https://github.com/firecrawl/firecrawl",
        }}
        sideLabel="Open Source"
      />
    ),
  },
];
