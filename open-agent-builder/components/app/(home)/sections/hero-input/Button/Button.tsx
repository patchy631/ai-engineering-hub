import { AnimatePresence, motion } from "motion/react";

import AnimatedWidth from "@/components/shared/layout/animated-width";
import ArrowRight from "@/components/app/(home)/sections/hero-input/_svg/ArrowRight";
import Button from "@/components/shared/button/Button";

export default function HeroInputSubmitButton({
  tab,
  dirty,
}: {
  tab: string;
  dirty: boolean;
}) {
  return (
    <Button className="hero-input-button !p-0 bg-heat-100 hover:bg-heat-200" size="large" variant="primary">
      <AnimatedWidth>
        <AnimatePresence initial={false} mode="popLayout">
          <motion.div
            animate={{ opacity: 1, x: 0, filter: "blur(0px)" }}
            exit={{ opacity: 0, x: -10, filter: "blur(2px)" }}
            initial={{ opacity: 0, x: 10, filter: "blur(2px)" }}
            key={dirty ? "dirty" : "clean"}
          >
            {dirty ? (
              <div className="py-8 w-126 text-center text-white">Start building</div>
            ) : (
              <div className="w-60 py-8 flex-center">
                <ArrowRight />
              </div>
            )}
          </motion.div>
        </AnimatePresence>
      </AnimatedWidth>
    </Button>
  );
}
