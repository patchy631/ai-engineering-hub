"use client";

import type { Transition, Variants } from "framer-motion";
import { motion, useAnimation } from "framer-motion";
import { useCallback, useEffect } from "react";

const playIconVariants: Variants = {
  normal: {
    x: 0,
    rotate: 0,
  },
  animate: {
    x: [0, -1, 2, 0],
    rotate: [0, -10, 0, 0],
    transition: {
      duration: 0.5,
      times: [0, 0.2, 0.5, 1],
      stiffness: 260,
      damping: 20,
    },
  },
};

const defaultTransition: Transition = {
  duration: 0.6,
  opacity: { duration: 0.2 },
};

const pathVariants: Variants = {
  normal: {
    pathLength: 1,
    opacity: 1,
  },
  animate: {
    opacity: [0, 1],
    pathLength: [0.5, 1],
  },
};

// Higher-order component for icon animation
const withIconAnimation = (IconComponent: React.ComponentType<any>) => {
  return ({
    isHovered = false,
    className,
    ...props
  }: {
    isHovered?: boolean;
    className?: string;
  }) => {
    const controls = useAnimation();

    useEffect(() => {
      if (isHovered) {
        controls.start("animate");
      } else {
        controls.start("normal");
      }
    }, [isHovered, controls]);

    return (
      <div className={className}>
        <IconComponent controls={controls} {...props} />
      </div>
    );
  };
};

// Higher-order component for icon animation
const withChartIconAnimation = (IconComponent: React.ComponentType<any>) => {
  return ({
    isHovered = false,
    className,
    ...props
  }: {
    isHovered?: boolean;
    className?: string;
  }) => {
    const controls = useAnimation();

    const handleHoverStart = async () => {
      await controls.start((i) => ({
        pathLength: 0,
        opacity: 0,
        transition: { delay: i * 0.1, duration: 0.3 },
      }));
      await controls.start((i) => ({
        pathLength: 1,
        opacity: 1,
        transition: { delay: i * 0.1, duration: 0.3 },
      }));
    };

    useEffect(() => {
      if (isHovered) {
        handleHoverStart();
      } else {
        handleHoverEnd();
      }
    }, [isHovered, handleHoverStart]);

    const handleHoverEnd = () => {
      controls.start("normal");
    };

    return (
      <div className={className}>
        <IconComponent
          onMouseEnter={handleHoverStart}
          onMouseLeave={handleHoverEnd}
          controls={controls}
          {...props}
        />
      </div>
    );
  };
};

// Base icon components
const HomeIconBase = ({ controls }: { controls: any }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="16"
    height="16"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <path d="M3 10a2 2 0 0 1 .709-1.528l7-5.999a2 2 0 0 1 2.582 0l7 5.999A2 2 0 0 1 21 10v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
    <motion.path
      d="M15 21v-8a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v8"
      variants={pathVariants}
      transition={defaultTransition}
      animate={controls}
    />
  </svg>
);

// Example of another icon with animation
const PlayIconBase = ({ controls }: { controls: any }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="16"
    height="16"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <motion.path
      d="M5 3l14 9-14 9V3z"
      variants={playIconVariants}
      transition={defaultTransition}
      animate={controls}
    />
  </svg>
);

const SettingsGearIconBase = ({ controls }: { controls: any }) => {
  return (
    <motion.svg
      xmlns="http://www.w3.org/2000/svg"
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      transition={{ type: "spring", stiffness: 50, damping: 10 }}
      variants={{
        normal: {
          rotate: 0,
        },
        animate: {
          rotate: 90,
        },
      }}
      animate={controls}
    >
      <path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z" />
      <circle cx="12" cy="12" r="3" />
    </motion.svg>
  );
};

const lineChartVariants2: Variants = {
  visible: { pathLength: 1, opacity: 1 },
  hidden: { pathLength: 0, opacity: 0 },
};
const ChartColumnIconBase = ({ controls }: { controls: any }) => {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <motion.path
        d="M13 17V9"
        variants={lineChartVariants2}
        transition={defaultTransition}
        animate={controls}
        initial="visible"
        custom={1}
      />
      <motion.path
        d="M18 17V5"
        variants={lineChartVariants2}
        transition={defaultTransition}
        animate={controls}
        initial="visible"
        custom={2}
      />
      <path d="M3 3v16a2 2 0 0 0 2 2h16" />
      <motion.path
        d="M8 17v-3"
        variants={lineChartVariants2}
        transition={defaultTransition}
        animate={controls}
        initial="visible"
        custom={0}
      />
    </svg>
  );
};

// const defaultTransition: Transition = {
//   duration: 0.9,
//   ease: 'easeInOut',
// };

// const pathVariants: Variants = {
//   normal: {
//     rotate: 0,
//     x: 0,
//     y: 0,
//   },
//   hover: {
//     rotate: [0, 4, 2, -3, 1, 0],
//     x: [0, 0.7, -0.3, 0.5, 0.2, 0],
//     y: [0, -0.2, 0.3, -0.2, 0.4, 0],
//   },
// };

const transition = (custom: number): Transition => ({
  duration: 0.25,
  delay: custom * 0.1,
});

const variants: Variants = {
  default: {
    pathLength: 1,
    opacity: 1,
  },
  normal: (custom: number) => ({
    pathLength: 1,
    opacity: 1,
    transition: transition(custom),
  }),
  animate: (custom: number) => ({
    pathLength: 0.5,
    opacity: 1,
    transition: transition(custom),
  }),
};

const ActivityLogsIconBase = ({ controls }: { controls: any }) => {
  return (
    <svg
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      xmlns="http://www.w3.org/2000/svg"
    >
      <motion.rect
        variants={variants}
        initial="normal"
        animate={controls}
        custom={0}
        x="3"
        y="3"
        width="3"
        height="3"
        fill="currentColor"
        stroke="none"
      />
      <motion.path
        variants={variants}
        initial="normal"
        animate={controls}
        custom={0}
        d="M8 4.5 L21 4.5"
        strokeWidth="2"
      />

      <motion.rect
        variants={variants}
        initial="normal"
        animate={controls}
        custom={1}
        x="3"
        y="10"
        width="3"
        height="3"
        fill="currentColor"
        stroke="none"
      />
      <motion.path
        variants={variants}
        initial="normal"
        animate={controls}
        custom={1}
        d="M8 11.5 L21 11.5"
        strokeWidth="2"
      />

      <motion.rect
        variants={variants}
        initial="normal"
        animate={controls}
        custom={2}
        x="3"
        y="17"
        width="3"
        height="3"
        fill="currentColor"
        stroke="none"
      />
      <motion.path
        variants={variants}
        initial="normal"
        animate={controls}
        custom={2}
        d="M8 18.5 L21 18.5"
        strokeWidth="2"
      />
    </svg>
  );
};

const defaultTransition2: Transition = {
  type: "spring",
  stiffness: 200,
  damping: 10,
};

const pathVariants2: Variants = {
  normal: {
    rotate: 0,
  },
  animate: {
    rotate: -20,
  },
};

const KeyOneBase = ({ controls }: { controls: any }) => {
  return (
    <motion.svg
      viewBox="0 0 24 24"
      xmlns="http://www.w3.org/2000/svg"
      width="16"
      height="16"
      fill="currentColor"
      aria-hidden="true"
      animate={controls}
      initial="normal"
      variants={pathVariants2}
      transition={defaultTransition2}
    >
      <path d="M10.7577 11.8281L18.6066 3.97919L20.0208 5.3934L18.6066 6.80761L21.0815 9.28249L19.6673 10.6967L17.1924 8.22183L15.7782 9.63604L17.8995 11.7574L16.4853 13.1716L14.364 11.0503L12.1719 13.2423C13.4581 15.1837 13.246 17.8251 11.5355 19.5355C9.58291 21.4882 6.41709 21.4882 4.46447 19.5355C2.51184 17.5829 2.51184 14.4171 4.46447 12.4645C6.17493 10.754 8.81633 10.5419 10.7577 11.8281ZM10.1213 18.1213C11.2929 16.9497 11.2929 15.0503 10.1213 13.8787C8.94975 12.7071 7.05025 12.7071 5.87868 13.8787C4.70711 15.0503 4.70711 16.9497 5.87868 18.1213C7.05025 19.2929 8.94975 19.2929 10.1213 18.1213Z" />
    </motion.svg>
  );
};

const frameVariants: Variants = {
  normal: { opacity: 1 },
  animate: { opacity: 1 },
};

const lineVariants: Variants = {
  normal: { pathLength: 1, opacity: 1 },
  animate: { pathLength: 0, opacity: 0 },
};

const ScanTextIconBase = ({ controls }: { controls: any }) => {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <motion.path
        d="M3 7V5a2 2 0 0 1 2-2h2"
        variants={frameVariants}
        animate={controls}
      />
      <motion.path
        d="M17 3h2a2 2 0 0 1 2 2v2"
        variants={frameVariants}
        animate={controls}
      />
      <motion.path
        d="M21 17v2a2 2 0 0 1-2 2h-2"
        variants={frameVariants}
        animate={controls}
      />
      <motion.path
        d="M7 21H5a2 2 0 0 1-2-2v-2"
        variants={frameVariants}
        animate={controls}
      />
      <motion.path
        d="M7 8h8"
        variants={lineVariants}
        initial="animate"
        animate={controls}
        custom={0}
      />
      <motion.path
        d="M7 12h10"
        variants={lineVariants}
        initial="animate"
        animate={controls}
        custom={1}
      />
      <motion.path
        d="M7 16h6"
        variants={lineVariants}
        initial="animate"
        animate={controls}
        custom={2}
      />
    </svg>
  );
};

// Create animated versions of icons
const HomeIcon = withIconAnimation(HomeIconBase);
const PlayIcon = withIconAnimation(PlayIconBase);
const SettingsGearIcon = withIconAnimation(SettingsGearIconBase);
const ChartColumnIcon = withChartIconAnimation(ChartColumnIconBase);
const ActivityLogsIcon = withIconAnimation(ActivityLogsIconBase);
const ScanTextIcon = withIconAnimation(ScanTextIconBase);
const KeyIcon = withIconAnimation(KeyOneBase);

// Logout icon with animation
const LogOutIconBase = ({ controls }: { controls: any }) => {
  return (
    <motion.svg
      xmlns="http://www.w3.org/2000/svg"
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
      <motion.polyline
        points="16 17 21 12 16 7"
        variants={{
          normal: { x: 0 },
          animate: { x: [0, 3, 0] },
        }}
        transition={{ duration: 0.5, ease: "easeInOut" }}
        animate={controls}
      />
      <motion.line
        x1="21"
        y1="12"
        x2="9"
        y2="12"
        variants={{
          normal: { x1: 21, x2: 9 },
          animate: { x1: [21, 24, 21], x2: [9, 12, 9] },
        }}
        transition={{ duration: 0.5, ease: "easeInOut" }}
        animate={controls}
      />
    </motion.svg>
  );
};

// External link icon with animation
const ExternalLinkIconBase = ({ controls }: { controls: any }) => {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
      <motion.polyline
        points="15 3 21 3 21 9"
        variants={{
          normal: { rotate: 0, scale: 1 },
          animate: { rotate: [0, -10, 0], scale: [1, 1.1, 1] },
        }}
        transition={{ duration: 0.4, ease: "easeInOut" }}
        animate={controls}
      />
      <motion.line
        x1="10"
        y1="14"
        x2="21"
        y2="3"
        variants={pathVariants}
        transition={defaultTransition}
        animate={controls}
      />
    </svg>
  );
};

// File text icon with animation
const FileTextIconBase = ({ controls }: { controls: any }) => {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
      <motion.polyline
        points="14 2 14 8 20 8"
        variants={{
          normal: { pathLength: 1, opacity: 1 },
          animate: { pathLength: [1, 0, 1], opacity: [1, 0.5, 1] },
        }}
        transition={{ duration: 0.6, ease: "easeInOut" }}
        animate={controls}
      />
      <motion.line
        x1="16"
        y1="13"
        x2="8"
        y2="13"
        variants={lineVariants}
        initial="animate"
        animate={controls}
        custom={0}
      />
      <motion.line
        x1="16"
        y1="17"
        x2="8"
        y2="17"
        variants={lineVariants}
        initial="animate"
        animate={controls}
        custom={1}
      />
    </svg>
  );
};

// Book open icon with animation
const BookOpenIconBase = ({ controls }: { controls: any }) => {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <motion.path
        d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"
        variants={{
          normal: { rotate: 0 },
          animate: { rotate: [-2, 2, -2] },
        }}
        transition={{ duration: 0.6, ease: "easeInOut" }}
        animate={controls}
      />
      <motion.path
        d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"
        variants={{
          normal: { rotate: 0 },
          animate: { rotate: [2, -2, 2] },
        }}
        transition={{ duration: 0.6, ease: "easeInOut" }}
        animate={controls}
      />
    </svg>
  );
};

// Message square icon with animation
const MessageSquareIconBase = ({ controls }: { controls: any }) => {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
      <motion.circle
        cx="8"
        cy="10"
        r="1"
        fill="currentColor"
        variants={{
          normal: { scale: 1, opacity: 1 },
          animate: { scale: [1, 1.5, 1], opacity: [1, 0.5, 1] },
        }}
        transition={{ duration: 0.4, delay: 0 }}
        animate={controls}
      />
      <motion.circle
        cx="12"
        cy="10"
        r="1"
        fill="currentColor"
        variants={{
          normal: { scale: 1, opacity: 1 },
          animate: { scale: [1, 1.5, 1], opacity: [1, 0.5, 1] },
        }}
        transition={{ duration: 0.4, delay: 0.1 }}
        animate={controls}
      />
      <motion.circle
        cx="16"
        cy="10"
        r="1"
        fill="currentColor"
        variants={{
          normal: { scale: 1, opacity: 1 },
          animate: { scale: [1, 1.5, 1], opacity: [1, 0.5, 1] },
        }}
        transition={{ duration: 0.4, delay: 0.2 }}
        animate={controls}
      />
    </svg>
  );
};

const LogOutIcon = withIconAnimation(LogOutIconBase);
const ExternalLinkIcon = withIconAnimation(ExternalLinkIconBase);
const FileTextIcon = withIconAnimation(FileTextIconBase);
const BookOpenIcon = withIconAnimation(BookOpenIconBase);
const MessageSquareIcon = withIconAnimation(MessageSquareIconBase);

// Bell icon with animation
const BellIconBase = ({ controls }: { controls: any }) => {
  return (
    <motion.svg
      xmlns="http://www.w3.org/2000/svg"
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <motion.path
        d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"
        variants={{
          normal: { rotate: 0 },
          animate: { rotate: [-10, 10, -10, 10, 0] },
        }}
        transition={{ duration: 0.5, ease: "easeInOut" }}
        animate={controls}
        style={{ transformOrigin: "50% 20%" }}
      />
      <motion.path
        d="M10.3 21a1.94 1.94 0 0 0 3.4 0"
        variants={{
          normal: { scale: 1 },
          animate: { scale: [1, 1.1, 1] },
        }}
        transition={{ duration: 0.5, ease: "easeInOut" }}
        animate={controls}
      />
    </motion.svg>
  );
};

// Gift icon with animation
const GiftIconBase = ({ controls }: { controls: any }) => {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      {/* Gift box bottom */}
      <polyline points="20 12 20 22 4 22 4 12" />
      <line x1="12" y1="22" x2="12" y2="12" />

      {/* Gift lid with opening animation */}
      <motion.g
        variants={{
          normal: { y: 0, rotate: 0 },
          animate: { y: -3, rotate: -8 },
        }}
        transition={{ duration: 0.4, ease: "easeOut" }}
        animate={controls}
        style={{ transformOrigin: "2px 9px" }}
      >
        <rect x="2" y="7" width="20" height="5" />
        <line x1="12" y1="7" x2="12" y2="12" />

        {/* Left bow */}
        <motion.path
          d="M12 7H7.5a2.5 2.5 0 0 1 0-5C11 2 12 7 12 7z"
          variants={{
            normal: { scale: 1 },
            animate: { scale: [1, 1.1, 1] },
          }}
          transition={{ duration: 0.4, ease: "easeInOut" }}
        />

        {/* Right bow */}
        <motion.path
          d="M12 7h4.5a2.5 2.5 0 0 0 0-5C13 2 12 7 12 7z"
          variants={{
            normal: { scale: 1 },
            animate: { scale: [1, 1.1, 1] },
          }}
          transition={{ duration: 0.4, ease: "easeInOut" }}
        />
      </motion.g>
    </svg>
  );
};

// HelpCircle icon with animation
const HelpCircleIconBase = ({ controls }: { controls: any }) => {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <motion.circle
        cx="12"
        cy="12"
        r="10"
        variants={{
          normal: { rotate: 0 },
          animate: { rotate: 360 },
        }}
        transition={{ duration: 0.6, ease: "easeInOut" }}
        animate={controls}
      />
      <motion.path
        d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"
        variants={{
          normal: { opacity: 1 },
          animate: { opacity: [1, 0.5, 1] },
        }}
        transition={{ duration: 0.4, ease: "easeInOut" }}
        animate={controls}
      />
      <motion.line
        x1="12"
        y1="17"
        x2="12.01"
        y2="17"
        variants={{
          normal: { scale: 1 },
          animate: { scale: [1, 1.5, 1] },
        }}
        transition={{ duration: 0.4, ease: "easeInOut", delay: 0.2 }}
        animate={controls}
      />
    </svg>
  );
};

const BellIcon = withIconAnimation(BellIconBase);
const GiftIcon = withIconAnimation(GiftIconBase);
const HelpCircleIcon = withIconAnimation(HelpCircleIconBase);

// SquareArrowUp icon with animation (for Upgrade button)
const SquareArrowUpIconBase = ({ controls }: { controls: any }) => {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <rect width="18" height="18" x="3" y="3" rx="2" />
      <motion.path
        d="m8 12 4-4 4 4"
        variants={{
          normal: { y: 0 },
          animate: { y: [-2, 0] },
        }}
        transition={{ duration: 0.3, ease: "easeOut" }}
        animate={controls}
      />
      <motion.path
        d="M12 16V8"
        variants={{
          normal: { scaleY: 1 },
          animate: { scaleY: [0.8, 1] },
        }}
        transition={{ duration: 0.3, ease: "easeOut" }}
        animate={controls}
        style={{ transformOrigin: "50% 100%" }}
      />
    </svg>
  );
};

const SquareArrowUpIcon = withIconAnimation(SquareArrowUpIconBase);

// Code icon with animation
const CodeIconBase = ({ controls }: { controls: any }) => {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <motion.polyline
        points="16 18 22 12 16 6"
        variants={{
          normal: { x: 0 },
          animate: { x: [0, 2, 0] },
        }}
        transition={{ duration: 0.4, ease: "easeInOut" }}
        animate={controls}
      />
      <motion.polyline
        points="8 6 2 12 8 18"
        variants={{
          normal: { x: 0 },
          animate: { x: [0, -2, 0] },
        }}
        transition={{ duration: 0.4, ease: "easeInOut" }}
        animate={controls}
      />
    </svg>
  );
};

const CodeIcon = withIconAnimation(CodeIconBase);

// TestTube icon for Extract Playground (Lucide TestTube2 icon without bubble)
const BeakerIconBase = ({ controls }: { controls: any }) => {
  return (
    <motion.svg
      xmlns="http://www.w3.org/2000/svg"
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      variants={{
        normal: { rotate: 0 },
        animate: { rotate: [-8, 8, -8] },
      }}
      transition={{
        duration: 0.8,
        ease: "easeInOut",
        times: [0, 0.5, 1],
      }}
      animate={controls}
    >
      <path d="M21 7 6.82 21.18a2.83 2.83 0 0 1-3.99-.01v0a2.83 2.83 0 0 1 0-4L17 3" />
      <path d="m16 2 6 6" />
    </motion.svg>
  );
};

const BeakerIcon = withIconAnimation(BeakerIconBase);

export {
  HomeIcon,
  PlayIcon,
  SettingsGearIcon,
  ChartColumnIcon,
  ActivityLogsIcon,
  KeyIcon,
  ScanTextIcon,
  LogOutIcon,
  ExternalLinkIcon,
  FileTextIcon,
  BookOpenIcon,
  MessageSquareIcon,
  BellIcon,
  GiftIcon,
  HelpCircleIcon,
  SquareArrowUpIcon,
  CodeIcon,
  BeakerIcon,
};
