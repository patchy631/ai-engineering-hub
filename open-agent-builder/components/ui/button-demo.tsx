import Button from "./shadcn/button";

export function ButtonDemo() {
  return (
    <div className="p-8 space-y-8 bg-white">
      <div>
        <h2 className="text-title-h5 mb-4">Button Component - Two Variants</h2>
        <p className="text-body-medium text-black-alpha-64 mb-6">
          Unified button system with only two variants: Primary (orange/heat) and Secondary (grey)
        </p>
      </div>

      {/* Primary Buttons */}
      <div className="space-y-4">
        <h3 className="text-label-large text-accent-black">Primary Variant (Orange)</h3>
        <div className="flex items-center gap-12">
          <Button variant="primary">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <rect width="18" height="18" x="3" y="3" rx="2"></rect>
              <path d="m8 12 4-4 4 4"></path>
              <path d="M12 16V8"></path>
            </svg>
            <span>Upgrade</span>
          </Button>

          <Button variant="primary">
            <span>Get Started</span>
          </Button>

          <Button variant="primary" disabled>
            <span>Disabled</span>
          </Button>

          <Button variant="primary" isLoading>
            <span>Loading</span>
          </Button>
        </div>
      </div>

      {/* Secondary Buttons */}
      <div className="space-y-4">
        <h3 className="text-label-large text-accent-black">Secondary Variant (Grey)</h3>
        <div className="flex items-center gap-12">
          <Button variant="secondary">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-16 h-16">
              <path d="M10.268 21a2 2 0 0 0 3.464 0"></path>
              <path d="M3.262 15.326A1 1 0 0 0 4 17h16a1 1 0 0 0 .74-1.673C19.41 13.956 18 12.499 18 8A6 6 0 0 0 6 8c0 4.499-1.411 5.956-2.738 7.326"></path>
            </svg>
            <span className="relative">
              Notifications
              <span className="absolute -right-4 -top-10 flex h-20 w-20 items-center justify-center rounded-full bg-heat-100 text-white text-10 font-semibold z-10">1</span>
            </span>
          </Button>

          <Button variant="secondary">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-16 h-16">
              <circle cx="12" cy="12" r="10"></circle>
              <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path>
              <path d="M12 17h.01"></path>
            </svg>
            <span>Help</span>
          </Button>

          <Button variant="secondary">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"></path>
              <path d="M14 2v4a2 2 0 0 0 2 2h4"></path>
              <path d="M10 9H8"></path>
              <path d="M16 13H8"></path>
              <path d="M16 17H8"></path>
            </svg>
            <span>Docs</span>
          </Button>

          <Button variant="secondary" disabled>
            <span>Disabled</span>
          </Button>

          <Button variant="secondary" isLoading>
            <span>Loading</span>
          </Button>
        </div>
      </div>

      {/* Mixed Usage Example */}
      <div className="space-y-4">
        <h3 className="text-label-large text-accent-black">Mixed Usage Example</h3>
        <div className="flex items-center gap-12">
          <Button variant="secondary">Cancel</Button>
          <Button variant="primary">Save Changes</Button>
        </div>
      </div>

      {/* Size Variations */}
      <div className="space-y-4">
        <h3 className="text-label-large text-accent-black">Size Variations</h3>
        <div className="flex items-center gap-12">
          <div className="space-y-2">
            <p className="text-label-small text-black-alpha-64">Default Size</p>
            <div className="flex gap-4">
              <Button variant="secondary" size="default">Secondary</Button>
              <Button variant="primary" size="default">Primary</Button>
            </div>
          </div>
          <div className="space-y-2">
            <p className="text-label-small text-black-alpha-64">Large Size (Default)</p>
            <div className="flex gap-4">
              <Button variant="secondary" size="large">Secondary</Button>
              <Button variant="primary" size="large">Primary</Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}