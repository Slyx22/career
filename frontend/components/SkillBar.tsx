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
        <span className="font-body text-sm text-ink">
          {item.name}
          {level && !item.is_tool && (
            <span
              className={`ml-2 rounded px-1.5 py-0.5 align-middle text-[10px] font-medium uppercase tracking-wide ${
                item.importance_level === "essential"
                  ? "bg-ink text-paper"
                  : item.importance_level === "important"
                  ? "bg-brass/20 text-brass-dark"
                  : "bg-line text-slate-600"
              }`}
            >
              {level}
            </span>
          )}
        </span>
        <span className="shrink-0 font-body text-xs text-slate-600">
          {item.present ? `${item.score_percent}%` : "not found in CV"}
        </span>
      </div>
      <div
        className="relative h-2 w-full overflow-hidden rounded-sm bg-line"
        role="progressbar"
        aria-valuenow={item.present ? item.score_percent : 0}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label={item.name}
      >
        <div
          className={`h-full rounded-sm ${item.present ? "bg-brass" : "bg-transparent"}`}
          style={{ width: `${item.present ? item.score_percent : 0}%` }}
        />
      </div>
      {(!item.present || weak) && item.tip && (
        <p className="mt-1.5 font-body text-xs text-slate-600">
          <span className="font-medium text-ink">{weak ? "Make it stronger: " : "How to show it: "}</span>
          {item.tip}
        </p>
      )}
    </div>
  );
}
