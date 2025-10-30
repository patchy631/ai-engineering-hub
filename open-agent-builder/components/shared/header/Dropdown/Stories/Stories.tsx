import ArrowUp from "./_svg/ArrowUp";
import Replit from "./_svg/Replit";
import StoriesFlame from "./Flame/Flame";

export default function HeaderDropdownStories() {
  return (
    <a
      className="pt-32 pr-32 pl-44 pb-48 group block border-b border-border-faint relative overflow-clip"
      href="/blog/how-replit-uses-firecrawl-to-power-ai-agents"
    >
      <div className="flex mb-40 justify-between items-center">
        <div className="py-4 px-8 text-heat-100 text-[12px]/[16px] font-[450] bg-heat-8 rounded-6">
          Customer story
        </div>

        <div className="p-2 text-black-alpha-56 group-hover:text-heat-100 transition-all group-hover:translate-x-1 group-hover:translate-y-[-1px]">
          <ArrowUp />
        </div>
      </div>

      <Replit />

      <div className="text-title-h5 mt-31 pr-32">
        How Replit uses <span className="text-heat-100">Firecrawl</span> to
        power Replit Agent
      </div>

      <StoriesFlame />
    </a>
  );
}
