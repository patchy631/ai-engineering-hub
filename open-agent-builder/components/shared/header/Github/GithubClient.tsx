"use client";

import Button from "@/components/ui/shadcn/button";
import GithubIcon from "./_svg/GithubIcon";

export default function HeaderGithubClient() {
  return (
    <a
      className="contents"
      href="https://github.com/firecrawl/firecrawl"
      target="_blank"
    >
      <Button variant="secondary">
        <GithubIcon />
        21.5k
      </Button>
    </a>
  );
}