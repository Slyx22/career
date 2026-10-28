"use client";

import { useState } from "react";

interface FeatureOption {
  key: string;
  icon: string;
  label: string;
  description: string;
}

const FEATURES: FeatureOption[] = [
  {
    key: "personalized_roadmap",
    icon: "🗺️",
    label: "Get my personalised improvement roadmap",
    description: "Step-by-step plan tailored to your current skills",
  },
  {
    key: "employer_insights",
    icon: "💼",
    label: "See what employers look for in this career",
    description: "Real job posting data and hiring trends",
  },
  {
    key: "score_increase_tips",
    icon: "📈",
    label: "See how I can increase my score",
    description: "Detailed actions to boost your readiness",
  },
  {
    key: "cv_improvement",
    icon: "📄",
    label: "Improve my CV",
    description: "AI-powered suggestions to strengthen your CV",
  },
  {
    key: "profile_integration",
    icon: "🔗",
    label: "Connect my professional profiles",
    description: "Link LinkedIn, GitHub, and other profiles",
  },
  {
    key: "download_certificate",
    icon: "🏆",
    label: "Download my certificate",
    description: "Professional certificate of your readiness score",
  },
];

interface Props {
  analysisId: string;
}

export function FeatureInterestSurvey({ analysisId }: Props) {
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [submitted, setSubmitted] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  async function handleClick(featureKey: string) {
    if (submitted) return;

    // Optimistic update
    const newSelected = new Set(selected);
    if (newSelected.has(featureKey)) {
      newSelected.delete(featureKey);
    } else {
      newSelected.add(featureKey);
    }
    setSelected(newSelected);

    // Send to backend
    try {
      await fetch("/api/feature-interest", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ analysisId, featureKey }),
      });
    } catch (error) {
      // Silently fail - this is optional tracking
      console.error("Failed to save feature interest:", error);
    }
  }

  async function handleNotifyMe() {
    setSubmitting(true);
    // In the future, this could prompt for email to notify when features launch
    setTimeout(() => {
      setSubmitted(true);
      setSubmitting(false);
    }, 500);
  }

  if (submitted) {
    return (
      <div className="glass-sheet p-6 text-center sm:p-8">
        <p className="font-display text-lg font-semibold">Thanks, noted</p>
        <p className="mt-2 text-sm text-slate">
          We'll prioritize the features you selected. Check back soon!
        </p>
      </div>
    );
  }

  return (
    <div className="glass-sheet p-6 sm:p-8">
      <h3 className="font-display text-xl font-semibold tracking-tight">
        What would you like to do next?
      </h3>
      <p className="mt-1 text-sm text-slate">
        These features are coming soon. Select what interests you most to help
        us prioritize.
      </p>

      <div className="mt-6 grid grid-cols-1 gap-3 md:grid-cols-2">
        {FEATURES.map((feature) => (
          <button
            key={feature.key}
            onClick={() => handleClick(feature.key)}
            className={`
              focus-ring group relative rounded-2xl border px-4 py-3 text-left transition-colors
              ${
                selected.has(feature.key)
                  ? "border-jacaranda/50 bg-jacaranda/10"
                  : "border-white/70 bg-white/50 hover:bg-white/75"
              }
            `}
          >
            <div className="flex items-start gap-3">
              <span className="text-xl">{feature.icon}</span>
              <div className="flex-1">
                <div className="flex flex-wrap items-center gap-x-2 gap-y-1">
                  <p className="text-sm font-medium">
                    {feature.label}
                  </p>
                  <span className="whitespace-nowrap rounded-full bg-brass/15 px-2 py-0.5 text-[11px] font-medium text-brass-dark">
                    Coming soon
                  </span>
                </div>
                <p className="mt-1 text-xs text-slate">
                  {feature.description}
                </p>
              </div>
              {selected.has(feature.key) && (
                <span className="text-jacaranda-dark">✓</span>
              )}
            </div>
          </button>
        ))}
      </div>

      {selected.size > 0 && (
        <button
          onClick={handleNotifyMe}
          disabled={submitting}
          className="btn-primary mt-6 w-full"
        >
          {submitting ? "Saving..." : "Notify me when these launch"}
        </button>
      )}
    </div>
  );
}
