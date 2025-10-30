"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, Save, Tag, FolderOpen, Clock, BarChart3, Globe, Lock, Info } from "lucide-react";
import { useMutation } from "convex/react";
import { api } from "@/convex/_generated/api";
import { toast } from "sonner";
import { useUser } from "@clerk/nextjs";

interface SaveAsTemplateModalProps {
  isOpen: boolean;
  onClose: () => void;
  workflowId: string;
  workflowName: string;
}

const categories = [
  "User Templates",
  "AI & Automation",
  "Data Processing",
  "Web Scraping",
  "Business Logic",
  "Integration",
  "Utility",
  "Custom",
];

const difficultyLevels = [
  { value: "beginner", label: "Beginner", color: "text-green-600" },
  { value: "intermediate", label: "Intermediate", color: "text-yellow-600" },
  { value: "advanced", label: "Advanced", color: "text-orange-600" },
  { value: "expert", label: "Expert", color: "text-red-600" },
];

export default function SaveAsTemplateModal({
  isOpen,
  onClose,
  workflowId,
  workflowName,
}: SaveAsTemplateModalProps) {
  const { user } = useUser();
  const saveAsTemplate = useMutation(api.templates.saveAsTemplate);

  const [formData, setFormData] = useState({
    name: `${workflowName} Template`,
    description: "",
    category: "User Templates",
    tags: [] as string[],
    difficulty: "intermediate",
    estimatedTime: "",
    isPublic: false,
  });

  const [currentTag, setCurrentTag] = useState("");
  const [isSaving, setIsSaving] = useState(false);

  const handleAddTag = () => {
    if (currentTag.trim() && !formData.tags.includes(currentTag.trim())) {
      setFormData({
        ...formData,
        tags: [...formData.tags, currentTag.trim()],
      });
      setCurrentTag("");
    }
  };

  const handleRemoveTag = (tag: string) => {
    setFormData({
      ...formData,
      tags: formData.tags.filter((t) => t !== tag),
    });
  };

  const handleSave = async () => {
    if (!formData.name.trim()) {
      toast.error("Template name is required");
      return;
    }

    if (!workflowId) {
      toast.error("Invalid workflow");
      return;
    }

    setIsSaving(true);

    try {
      await saveAsTemplate({
        workflowId: workflowId as any,
        name: formData.name,
        description: formData.description || undefined,
        category: formData.category,
        tags: formData.tags.length > 0 ? formData.tags : undefined,
        difficulty: formData.difficulty || undefined,
        estimatedTime: formData.estimatedTime || undefined,
        isPublic: formData.isPublic,
      });

      toast.success("Template saved successfully!", {
        description: formData.isPublic
          ? "Your template is now available to other users"
          : "Your template has been saved to your private collection",
      });

      onClose();
    } catch (error) {
      console.error("Failed to save template:", error);
      toast.error("Failed to save template", {
        description: error instanceof Error ? error.message : "Please try again",
      });
    } finally {
      setIsSaving(false);
    }
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/60 z-[100] flex items-center justify-center p-20"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.95, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.95, opacity: 0 }}
          transition={{ type: "spring", duration: 0.3 }}
          className="bg-accent-white rounded-16 shadow-2xl max-w-2xl w-full max-h-[85vh] overflow-hidden flex flex-col"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="p-24 border-b border-border-faint">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-12">
                <div className="w-40 h-40 rounded-10 bg-heat-100 flex items-center justify-center">
                  <Save className="w-20 h-20 text-white" />
                </div>
                <div>
                  <h2 className="text-title-h4 text-accent-black">Save as Template</h2>
                  <p className="text-body-small text-black-alpha-48 mt-2">
                    Save this workflow as a reusable template
                  </p>
                </div>
              </div>
              <button
                onClick={onClose}
                className="w-32 h-32 rounded-8 hover:bg-black-alpha-4 transition-colors flex items-center justify-center"
              >
                <X className="w-16 h-16" />
              </button>
            </div>
          </div>

          {/* Content */}
          <div className="p-24 overflow-y-auto flex-1 space-y-20">
            {/* Template Name */}
            <div>
              <label className="text-body-small font-medium text-accent-black mb-8 block">
                Template Name *
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="Enter template name"
                className="w-full px-12 py-10 bg-background-base border border-border-faint rounded-8 text-body-medium text-accent-black placeholder:text-black-alpha-32 focus:outline-none focus:ring-2 focus:ring-heat-100"
              />
            </div>

            {/* Description */}
            <div>
              <label className="text-body-small font-medium text-accent-black mb-8 block">
                Description
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Describe what this template does and when to use it"
                rows={3}
                className="w-full px-12 py-10 bg-background-base border border-border-faint rounded-8 text-body-medium text-accent-black placeholder:text-black-alpha-32 focus:outline-none focus:ring-2 focus:ring-heat-100 resize-none"
              />
            </div>

            {/* Category */}
            <div>
              <label className="text-body-small font-medium text-accent-black mb-8 flex items-center gap-6">
                <FolderOpen className="w-14 h-14" />
                Category
              </label>
              <select
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                className="w-full px-12 py-10 bg-background-base border border-border-faint rounded-8 text-body-medium text-accent-black focus:outline-none focus:ring-2 focus:ring-heat-100"
              >
                {categories.map((cat) => (
                  <option key={cat} value={cat}>
                    {cat}
                  </option>
                ))}
              </select>
            </div>

            {/* Tags */}
            <div>
              <label className="text-body-small font-medium text-accent-black mb-8 flex items-center gap-6">
                <Tag className="w-14 h-14" />
                Tags
              </label>
              <div className="flex gap-8 mb-8">
                <input
                  type="text"
                  value={currentTag}
                  onChange={(e) => setCurrentTag(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") {
                      e.preventDefault();
                      handleAddTag();
                    }
                  }}
                  placeholder="Add tags (press Enter)"
                  className="flex-1 px-12 py-10 bg-background-base border border-border-faint rounded-8 text-body-medium text-accent-black placeholder:text-black-alpha-32 focus:outline-none focus:ring-2 focus:ring-heat-100"
                />
                <button
                  onClick={handleAddTag}
                  className="px-16 py-10 bg-black-alpha-4 hover:bg-black-alpha-8 text-accent-black rounded-8 text-body-small font-medium transition-all"
                >
                  Add
                </button>
              </div>
              {formData.tags.length > 0 && (
                <div className="flex flex-wrap gap-6">
                  {formData.tags.map((tag) => (
                    <span
                      key={tag}
                      className="px-10 py-4 bg-heat-4 text-heat-100 rounded-6 text-body-small flex items-center gap-4"
                    >
                      {tag}
                      <button
                        onClick={() => handleRemoveTag(tag)}
                        className="hover:text-heat-200"
                      >
                        <X className="w-12 h-12" />
                      </button>
                    </span>
                  ))}
                </div>
              )}
            </div>

            {/* Difficulty & Time */}
            <div className="grid grid-cols-2 gap-16">
              <div>
                <label className="text-body-small font-medium text-accent-black mb-8 flex items-center gap-6">
                  <BarChart3 className="w-14 h-14" />
                  Difficulty
                </label>
                <select
                  value={formData.difficulty}
                  onChange={(e) => setFormData({ ...formData, difficulty: e.target.value })}
                  className="w-full px-12 py-10 bg-background-base border border-border-faint rounded-8 text-body-medium text-accent-black focus:outline-none focus:ring-2 focus:ring-heat-100"
                >
                  {difficultyLevels.map((level) => (
                    <option key={level.value} value={level.value}>
                      {level.label}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="text-body-small font-medium text-accent-black mb-8 flex items-center gap-6">
                  <Clock className="w-14 h-14" />
                  Estimated Time
                </label>
                <input
                  type="text"
                  value={formData.estimatedTime}
                  onChange={(e) => setFormData({ ...formData, estimatedTime: e.target.value })}
                  placeholder="e.g., 5-10 minutes"
                  className="w-full px-12 py-10 bg-background-base border border-border-faint rounded-8 text-body-medium text-accent-black placeholder:text-black-alpha-32 focus:outline-none focus:ring-2 focus:ring-heat-100"
                />
              </div>
            </div>

            {/* Visibility */}
            <div className="p-16 bg-background-base rounded-8 border border-border-faint">
              <div className="flex items-start gap-12">
                <input
                  type="checkbox"
                  id="isPublic"
                  checked={formData.isPublic}
                  onChange={(e) => setFormData({ ...formData, isPublic: e.target.checked })}
                  className="mt-4 w-16 h-16 rounded-4 border-border-faint text-heat-100 focus:ring-heat-100"
                />
                <label htmlFor="isPublic" className="flex-1 cursor-pointer">
                  <div className="flex items-center gap-8 mb-4">
                    {formData.isPublic ? (
                      <Globe className="w-16 h-16 text-heat-100" />
                    ) : (
                      <Lock className="w-16 h-16 text-black-alpha-48" />
                    )}
                    <span className="text-body-medium font-medium text-accent-black">
                      {formData.isPublic ? "Public Template" : "Private Template"}
                    </span>
                  </div>
                  <p className="text-body-small text-black-alpha-48">
                    {formData.isPublic
                      ? "This template will be visible to all users and can be used by anyone"
                      : "This template will only be visible to you"}
                  </p>
                </label>
              </div>
            </div>

            {/* Info Box */}
            <div className="p-16 bg-heat-4 border border-heat-100 rounded-8">
              <div className="flex items-start gap-12">
                <Info className="w-16 h-16 text-heat-100 flex-shrink-0 mt-2" />
                <div>
                  <p className="text-body-small text-accent-black">
                    Templates allow you to save and reuse workflow configurations. You can create
                    new workflows from your templates at any time.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="p-20 border-t border-border-faint bg-background-lighter flex justify-between">
            <button
              onClick={onClose}
              className="px-20 py-10 bg-black-alpha-4 hover:bg-black-alpha-8 text-accent-black rounded-8 text-body-medium font-medium transition-all"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              disabled={isSaving || !formData.name.trim()}
              className="px-20 py-10 bg-heat-100 hover:bg-heat-200 text-white rounded-8 text-body-medium font-medium transition-all active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-8"
            >
              {isSaving ? (
                <>
                  <div className="w-16 h-16 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <Save className="w-16 h-16" />
                  Save as Template
                </>
              )}
            </button>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}