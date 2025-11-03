"use client";

import Link from "next/link";
import { useState } from "react";

import Globe from "./_svg/Globe";
import HeroInputSubmitButton from "./Button/Button";
import HeroInputTabsMobile from "./Tabs/Mobile/Mobile";
import HeroInputTabs from "./Tabs/Tabs";
import AsciiExplosion from "@/components/shared/effects/flame/ascii-explosion";
import { Endpoint } from "@/components/shared/Playground/Context/types";

export default function HeroInput() {
  const [tab, setTab] = useState<Endpoint>(Endpoint.Scrape);
  const [url, setUrl] = useState<string>("");

  return (
    <div className="max-w-552 mx-auto w-full relative z-[11] lg:z-[2] rounded-20 lg:-mt-76">
      <div
        className="overlay bg-accent-white"
        style={{
          boxShadow:
            "0px 0px 44px 0px rgba(0, 0, 0, 0.02), 0px 88px 56px -20px rgba(0, 0, 0, 0.03), 0px 56px 56px -20px rgba(0, 0, 0, 0.02), 0px 32px 32px -20px rgba(0, 0, 0, 0.03), 0px 16px 24px -12px rgba(0, 0, 0, 0.03), 0px 0px 0px 1px rgba(0, 0, 0, 0.05), 0px 0px 0px 10px #F9F9F9",
        }}
      />

      <label className="p-16 flex gap-8 items-center w-full relative border-b border-black-alpha-5">
        <Globe />

        <input
          className="w-full bg-transparent text-body-input text-accent-black placeholder:text-black-alpha-48"
          placeholder="https://example.com"
          type="text"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              (
                document.querySelector(
                  ".hero-input-button",
                ) as HTMLButtonElement
              )?.click();
            }
          }}
        />
      </label>

      <div className="p-10 flex justify-between items-center relative">
        <HeroInputTabs
          setTab={setTab}
          tab={tab}
          allowedModes={[
            Endpoint.Scrape,
            Endpoint.Search,
            Endpoint.Map,
            Endpoint.Crawl,
          ]}
        />

        <HeroInputTabsMobile
          setTab={setTab}
          tab={tab}
          allowedModes={[
            Endpoint.Scrape,
            Endpoint.Search,
            Endpoint.Map,
            Endpoint.Crawl,
          ]}
        />

        <Link
          className="contents"
          href={`/playground?endpoint=${tab}&url=${url}&autorun=true`}
        >
          <HeroInputSubmitButton dirty={url.length > 0} tab={tab} />
        </Link>
      </div>

      <div className="h-248 top-84 cw-768 pointer-events-none absolute overflow-clip -z-10">
        <AsciiExplosion className="-top-200" />
      </div>
    </div>
  );
}
