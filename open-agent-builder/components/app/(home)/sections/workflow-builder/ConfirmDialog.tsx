"use client";

import { motion, AnimatePresence } from "framer-motion";

interface ConfirmDialogProps {
  isOpen: boolean;
  title: string;
  description: string;
  confirmText?: string;
  cancelText?: string;
  variant?: "danger" | "warning" | "default";
  onConfirm: () => void;
  onCancel: () => void;
}

export default function ConfirmDialog({
  isOpen,
  title,
  description,
  confirmText = "Confirm",
  cancelText = "Cancel",
  variant = "default",
  onConfirm,
  onCancel,
}: ConfirmDialogProps) {
  const handleConfirm = () => {
    onConfirm();
    onCancel(); // Close dialog
  };

  const variantStyles = {
    danger: {
      button: "bg-red-600 hover:bg-red-700 text-white",
      icon: "text-red-600",
      bg: "bg-red-50",
      border: "border-red-200",
    },
    warning: {
      button: "bg-yellow-600 hover:bg-yellow-700 text-white",
      icon: "text-yellow-600",
      bg: "bg-yellow-50",
      border: "border-yellow-200",
    },
    default: {
      button: "bg-heat-100 hover:bg-heat-200 text-white",
      icon: "text-heat-100",
      bg: "bg-heat-4",
      border: "border-heat-100",
    },
  };

  const styles = variantStyles[variant];

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black-alpha-48 z-[200] flex items-center justify-center p-20"
          onClick={onCancel}
        >
          <motion.div
            initial={{ scale: 0.95, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.95, opacity: 0 }}
            transition={{ duration: 0.2 }}
            onClick={(e) => e.stopPropagation()}
            className="bg-accent-white rounded-16 shadow-2xl max-w-400 w-full"
          >
            {/* Content */}
            <div className="p-24">
              <div className={`w-48 h-48 rounded-full ${styles.bg} border ${styles.border} flex items-center justify-center mb-16`}>
                <svg className={`w-24 h-24 ${styles.icon}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  {variant === "danger" ? (
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  ) : variant === "warning" ? (
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  ) : (
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  )}
                </svg>
              </div>

              <h2 className="text-title-h5 text-accent-black mb-8">{title}</h2>
              <p className="text-body-small text-black-alpha-48 mb-24">{description}</p>

              {/* Actions */}
              <div className="flex gap-12">
                <button
                  onClick={onCancel}
                  className="flex-1 px-16 py-10 bg-background-base hover:bg-black-alpha-4 border border-border-faint rounded-8 text-body-medium text-accent-black transition-colors"
                >
                  {cancelText}
                </button>
                <button
                  onClick={handleConfirm}
                  className={`flex-1 px-16 py-10 rounded-8 text-body-medium transition-all active:scale-[0.98] ${styles.button}`}
                >
                  {confirmText}
                </button>
              </div>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
