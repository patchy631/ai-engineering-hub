"use client";

import * as React from "react";
import * as SliderPrimitive from "@radix-ui/react-slider";
import { cn } from "@/utils/cn";

const Slider = React.forwardRef<
  React.ElementRef<typeof SliderPrimitive.Root>,
  React.ComponentPropsWithoutRef<typeof SliderPrimitive.Root>
>(({ className, ...props }, ref) => (
  <SliderPrimitive.Root
    ref={ref}
    className={cn(
      "relative flex w-full touch-none select-none items-center",
      className,
    )}
    {...props}
  >
    <SliderPrimitive.Track className="relative h-8 w-full grow overflow-hidden rounded-full bg-black-alpha-8">
      <SliderPrimitive.Range className="absolute h-full bg-heat-100" />
    </SliderPrimitive.Track>
    <SliderPrimitive.Thumb className="block h-20 w-20 rounded-full border-2 border-heat-100 bg-accent-white ring-offset-accent-white transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-heat-100 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50" />
  </SliderPrimitive.Root>
));

Slider.displayName = "Slider";

export { Slider };
