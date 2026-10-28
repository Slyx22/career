import { SkillBreakdownItem } from "@/lib/types";

const LEVEL_LABEL: Record<string, string> = {
  essential: "Essential",
  important: "Important",
  useful: "Useful",
};

export function SkillBar({ item }: { item: SkillBreakdownItem }) {
  const level = item.importance_level ? LEVEL_LABEL[item.importance_level] : "";
  const weak = item.present && item.score_percent < 35;
  return (
    <div className="py-3">
      <div className="mb-1.5 flex items-baseline justify-between gap-3">
        <span className="text-sm">
          {item.name}
          {level && !item.is_tool && (
            <span
              className={`ml-2 whitespace-nowrap rounded-full px-2 py-0.5 align-middle text-[11px] font-medium ${
                item.importance_level === "essential"
                  ? "bg-ink text-white"
                  : item.importance_level === "important"
                  ? "bg-jacaranda/15 text-jacaranda-dark"
                  : "bg-ink/[0.06] text-slate"
              }`}
            >
              {level}
            </span>
          )}
        </span>
        <span className="shrink-0 text-xs text-slate">
          {item.present ? `${item.score_percent}%` : "not found in CV"}
        </span>
      </div>
      <div
        className="relative h-2 w-full overflow-hidden rounded-full bg-ink/[0.07]"
        role="progressbar"
        aria-valuenow={item.present ? item.score_percent : 0}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label={item.name}
      >
        <div
          className={`h-full rounded-full ${item.present ? "bg-gradient-to-r from-jacaranda to-brass-light" : "bg-transparent"}`}
          style={{ width: `${item.present ? item.score_percent : 0}%` }}
        />
      </div>
      {(!item.present || weak) && item.tip && (
        <p className="mt-2 text-xs leading-relaxed text-slate">
          <span className="font-medium text-ink">{weak ? "Make it stronger: " : "How to show it: "}</span>
          {item.tip}
        </p>
      )}
    </div>
  );
}
