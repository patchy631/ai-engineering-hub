"use client";

import Link from "next/link";
import { useState, useEffect, Suspense } from "react";
import * as React from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { SignedIn, SignedOut, SignInButton, UserButton } from '@clerk/nextjs';

// Import shared components
import Button from "@/components/shared/button/Button";
import { Connector } from "@/components/shared/layout/curvy-rect";
import HeroFlame from "@/components/shared/effects/flame/hero-flame";
import AsciiExplosion from "@/components/shared/effects/flame/ascii-explosion";
import { HeaderProvider } from "@/components/shared/header/HeaderContext";

// Import hero section components
import HomeHeroBackground from "@/components/app/(home)/sections/hero/Background/Background";
import { BackgroundOuterPiece } from "@/components/app/(home)/sections/hero/Background/BackgroundOuterPiece";
import HomeHeroBadge from "@/components/app/(home)/sections/hero/Badge/Badge";
import HomeHeroPixi from "@/components/app/(home)/sections/hero/Pixi/Pixi";
import HomeHeroTitle from "@/components/app/(home)/sections/hero/Title/Title";
import HeroInputSubmitButton from "@/components/app/(home)/sections/hero-input/Button/Button";
import Globe from "@/components/app/(home)/sections/hero-input/_svg/Globe";
import { Endpoint } from "@/components/shared/Playground/Context/types";
import Step2Placeholder from "@/components/app/(home)/sections/step2/Step2Placeholder";
import WorkflowBuilder from "@/components/app/(home)/sections/workflow-builder/WorkflowBuilder";

// Import header components
import HeaderBrandKit from "@/components/shared/header/BrandKit/BrandKit";
import HeaderWrapper from "@/components/shared/header/Wrapper/Wrapper";
import HeaderDropdownWrapper from "@/components/shared/header/Dropdown/Wrapper/Wrapper";
import GithubIcon from "@/components/shared/header/Github/_svg/GithubIcon";
import ButtonUI from "@/components/ui/shadcn/button";

function StyleGuidePageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const [tab] = useState<Endpoint>(Endpoint.Scrape);
  const [url, setUrl] = useState<string>("");
  const [showStep2, setShowStep2] = useState(false);
  const [showWorkflowBuilder, setShowWorkflowBuilder] = useState(false);
  const [loadWorkflowId, setLoadWorkflowId] = useState<string | null>(null);
  const [loadTemplateId, setLoadTemplateId] = useState<string | null>(null);

  // Handle URL params
  useEffect(() => {
    if (!searchParams) return;

    const view = searchParams.get('view');
    const workflowId = searchParams.get('workflow');
    const templateId = searchParams.get('template');

    if (view === 'workflows') {
      setShowStep2(true);
      setShowWorkflowBuilder(false);
    } else if (workflowId) {
      setLoadWorkflowId(workflowId);
      setShowWorkflowBuilder(true);
      setShowStep2(false);
    } else if (templateId) {
      setLoadTemplateId(templateId);
      setShowWorkflowBuilder(true);
      setShowStep2(false);
    }
  }, [searchParams]);

  const handleSubmit = () => {
    setShowStep2(true);
    router.push('/?view=workflows');
  };

  const handleReset = () => {
    setShowStep2(false);
    setShowWorkflowBuilder(false);
    setLoadWorkflowId(null);
    setLoadTemplateId(null);
    setUrl("");
    router.push('/');
  };

  const handleCreateWorkflow = () => {
    setLoadWorkflowId(null);
    setLoadTemplateId(null);
    setShowWorkflowBuilder(true);
    router.push('/?view=builder');
  };

  return (
    <HeaderProvider>
      {showWorkflowBuilder ? (
        <SignedIn>
          <WorkflowBuilder
            onBack={handleReset}
            initialWorkflowId={loadWorkflowId}
            initialTemplateId={loadTemplateId}
          />
        </SignedIn>
      ) : (
      <div className="min-h-screen bg-background-base">
        {/* Header/Navigation Section */}
        <HeaderDropdownWrapper />
        
        <div className="sticky top-0 left-0 w-full z-[101] bg-background-base header">
          <div className="absolute top-0 cmw-container border-x border-border-faint h-full pointer-events-none" />
          
          <div className="h-1 bg-border-faint w-full left-0 -bottom-1 absolute" />
          
          <div className="cmw-container absolute h-full pointer-events-none top-0">
            <Connector className="absolute -left-[10.5px] -bottom-11" />
            <Connector className="absolute -right-[10.5px] -bottom-11" />
          </div>
          
          <HeaderWrapper>
            <div className="max-w-[900px] mx-auto w-full flex justify-between items-center">
              <div className="flex gap-24 items-center">
                <HeaderBrandKit />
              </div>
              
              <div className="flex gap-8 items-center">
                {/* GitHub Template Button */}
                <a
                  className="contents"
                  href="https://github.com/firecrawl/firecrawl"
                  target="_blank"
                >
                  <ButtonUI variant="secondary">
                    <GithubIcon />
                    Use this Template
                  </ButtonUI>
                </a>

                {/* Clerk Auth */}
                <SignedOut>
                  <SignInButton mode="modal">
                    <button className="px-16 py-8 bg-heat-100 hover:bg-heat-200 text-white rounded-8 text-body-medium font-medium transition-all active:scale-[0.98]">
                      Sign In
                    </button>
                  </SignInButton>
                </SignedOut>

                <SignedIn>
                  <UserButton
                    appearance={{
                      elements: {
                        avatarBox: "w-32 h-32",
                      }
                    }}
                    afterSignOutUrl="/"
                  />
                </SignedIn>
              </div>
            </div>
          </HeaderWrapper>
        </div>

        {/* Hero Section */}
        <section className="overflow-x-clip" id="home-hero">
          <div className="pt-28 lg:pt-254 lg:-mt-100 pb-115 relative" id="hero-content">
            <HomeHeroPixi />
            <HeroFlame />
            <BackgroundOuterPiece />
            <HomeHeroBackground />

            <AnimatePresence mode="wait">
              {!showStep2 ? (
                <motion.div
                  key="hero"
                  initial={{ opacity: 1 }}
                  exit={{ opacity: 0, scale: 0.95 }}
                  transition={{ duration: 0.5 }}
                  className="relative container px-16"
                >
                  <HomeHeroBadge />
                  <HomeHeroTitle />

                  <p className="text-center text-body-large">
                    Build intelligent web scraping workflows powered by AI.
                    <br className="lg-max:hidden" />
                    Turn any website into structured, agent-ready data.
                    <Link
                      className="bg-black-alpha-4 hover:bg-black-alpha-6 lg:ml-4 rounded-6 px-8 lg:px-6 text-label-large lg-max:py-2 h-30 lg:h-24 block lg-max:mt-8 lg-max:mx-auto lg-max:w-max lg:inline-block gap-4 transition-all"
                      href="https://firecrawl.dev"
                      target="_blank"
                    >
                      AI agent workflows
                    </Link>
                  </p>
                </motion.div>
              ) : (
                <SignedIn>
                  <motion.div
                    key="step2"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 0.5 }}
                    className="relative container px-16"
                  >
                    <Step2Placeholder
                      onReset={handleReset}
                      onCreateWorkflow={handleCreateWorkflow}
                      onLoadWorkflow={(id) => {
                        setLoadWorkflowId(id);
                        setLoadTemplateId(null);
                        setShowWorkflowBuilder(true);
                        router.push(`/?workflow=${id}`);
                      }}
                      onLoadTemplate={(templateId) => {
                        setLoadTemplateId(templateId);
                        setLoadWorkflowId(null);
                        setShowWorkflowBuilder(true);
                        router.push(`/?template=${templateId}`);
                      }}
                    />
                  </motion.div>
                </SignedIn>
              )}
            </AnimatePresence>
          </div>
          
          {/* Start Building Button */}
          {!showStep2 && (
            <motion.div
              className="flex justify-center -mt-90 relative z-10"
              initial={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.5 }}
            >
              {/* When signed in - navigate to workflows */}
              <SignedIn>
                <button
                  onClick={handleSubmit}
                  className="bg-heat-100 hover:bg-heat-200 text-white font-medium px-32 py-12 rounded-10 transition-all active:scale-[0.98] text-body-medium shadow-md cursor-pointer"
                >
                  Start building
                </button>
              </SignedIn>

              {/* When signed out - open sign-in modal */}
              <SignedOut>
                <SignInButton mode="modal">
                  <button className="bg-heat-100 hover:bg-heat-200 text-white font-medium px-32 py-12 rounded-10 transition-all active:scale-[0.98] text-body-medium shadow-md cursor-pointer">
                    Start building
                  </button>
                </SignInButton>
              </SignedOut>
            </motion.div>
          )}
        </section>
      </div>
      )}
    </HeaderProvider>
  );
}

export default function StyleGuidePage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <StyleGuidePageContent />
    </Suspense>
  );
}