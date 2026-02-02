"use client";

import { useState, useEffect, Suspense } from "react";
import * as React from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { SignedIn, SignedOut, SignInButton, UserButton } from '@clerk/nextjs';

// Import shared components
import { Connector } from "@/components/shared/layout/curvy-rect";
import { HeaderProvider } from "@/components/shared/header/HeaderContext";

// Import hero section components
import HomeHeroTitle from "@/components/app/(home)/sections/hero/Title/Title";
import { Endpoint } from "@/components/shared/Playground/Context/types";
import Step2Placeholder from "@/components/app/(home)/sections/step2/Step2Placeholder";
import WorkflowBuilder from "@/components/app/(home)/sections/workflow-builder/WorkflowBuilder";

// Import header components
import HeaderWrapper from "@/components/shared/header/Wrapper/Wrapper";
import HeaderDropdownWrapper from "@/components/shared/header/Dropdown/Wrapper/Wrapper";

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
    setLoadWorkflowId(null);
    setLoadTemplateId(null);
    setShowWorkflowBuilder(true);
    router.push('/?view=builder');
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
        
        <div className="sticky top-0 left-0 w-full z-[101] bg-purple-50 header">
          <div className="absolute top-0 cmw-container border-x border-border-faint h-full pointer-events-none" />

          <div className="h-1 bg-border-faint w-full left-0 -bottom-1 absolute" />

          <div className="cmw-container absolute h-full pointer-events-none top-0">
            <Connector className="absolute -left-[10.5px] -bottom-11" />
            <Connector className="absolute -right-[10.5px] -bottom-11" />
          </div>

          <HeaderWrapper>
            <div className="max-w-[900px] mx-auto w-full flex justify-between items-center">
              <div className="flex gap-24 items-center">
                {/* Logo removed */}
              </div>

              <div className="flex gap-8 items-center">
                {/* Powered by Composio Button */}
                <a
                  href="https://composio.dev/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-8 py-2.5 bg-[#de6f6f] hover:bg-[#d45f5f] text-white text-sm font-medium rounded-full transition-all shadow-sm hover:shadow-md"
                >
                  Powered by Composio
                </a>

                {/* Clerk Auth */}
                <SignedOut>
                  <SignInButton mode="modal">
                    <button className="px-16 py-8 bg-[#de6f6f] hover:bg-[#d45f5f] text-white rounded-8 text-body-medium font-medium transition-all active:scale-[0.98]">
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
        <section className="overflow-x-clip relative" id="home-hero">
          {/* Gradient Background */}
          <div className="absolute inset-0 bg-gradient-to-b from-purple-50 via-blue-50 to-background-base pointer-events-none" />
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-purple-100/20 via-transparent to-transparent pointer-events-none" />

          <div className="pt-28 lg:pt-254 lg:-mt-100 pb-115 relative" id="hero-content">
            <AnimatePresence mode="wait">
              {!showStep2 ? (
                <motion.div
                  key="hero"
                  initial={{ opacity: 1 }}
                  exit={{ opacity: 0, scale: 0.95 }}
                  transition={{ duration: 0.5 }}
                  className="relative container px-16"
                >
                  <HomeHeroTitle />

                  <p className="text-center text-body-large text-gray-700 max-w-2xl mx-auto mb-8">
                    Build custom AI agents without writing code.
                    <br className="lg-max:hidden" />
                    The open-source alternative to proprietary agent builders.
                  </p>

                  {/* Composio Branding */}
                  <div className="flex items-center justify-center mb-12">
                    <a
                      href="https://composio.dev/"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="px-6 py-3 bg-white rounded-full shadow-lg hover:shadow-xl border border-gray-200 text-sm transition-all cursor-pointer"
                      style={{
                        boxShadow: '0 4px 14px 0 rgba(124, 58, 237, 0.15), 0 2px 8px 0 rgba(59, 130, 246, 0.1)'
                      }}
                    >
                      <span className="text-gray-600">Powered by <span className="font-semibold text-[#de6f6f]">Composio&apos;s</span> self-evolving skill layer and 10k+ tools</span>
                    </a>
                  </div>
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
                  className="bg-[#de6f6f] hover:bg-[#d45f5f] text-white font-medium px-24 py-10 rounded-10 transition-all active:scale-[0.98] text-body-medium shadow-md cursor-pointer"
                >
                  Start building
                </button>
              </SignedIn>

              {/* When signed out - open sign-in modal */}
              <SignedOut>
                <SignInButton mode="modal">
                  <button className="bg-[#de6f6f] hover:bg-[#d45f5f] text-white font-medium px-24 py-10 rounded-10 transition-all active:scale-[0.98] text-body-medium shadow-md cursor-pointer">
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