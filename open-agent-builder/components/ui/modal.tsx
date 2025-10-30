import { ReactNode } from "react";

import { motion, AnimatePresence } from "motion/react";

export interface ModalProps {
  children?: ReactNode;
  contentClassName?: string;

  isOpen: boolean;
  setIsOpen: (open: boolean) => void;
}

export default function Modal({ children, isOpen, setIsOpen }: ModalProps) {
  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="!fixed inset-0 z-[1000] flex items-center justify-center p-4"
        >
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 bg-black/60 backdrop-blur-sm"
            onClick={() => setIsOpen(false)}
          />

          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            transition={{ type: "spring", damping: 25, stiffness: 300 }}
            className="max-w-lg w-full h-max overflow-y-auto max-h-[calc(100vh-64px)] bg-accent-white relative rounded-16 z-10"
            style={{
              boxShadow:
                "0px 32px 40px 6px rgba(0, 0, 0, 0.08), 0px 12px 32px 0px rgba(0, 0, 0, 0.06), 0px 24px 32px -8px rgba(0, 0, 0, 0.04), 0px 8px 16px -2px rgba(0, 0, 0, 0.04), 0px 0px 0px 1px rgba(0, 0, 0, 0.08)",
            }}
          >
            {children}
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
