import { SkillBreakdownItem } from "@/lib/types";

export function SkillBar({ item }: { item: SkillBreakdownItem }) {
  return (
    <div className="py-2.5">
      <div className="mb-1.5 flex items-baseline justify-between">
        <span className="font-body text-sm text-ink">{item.name}</span>
        <span className="font-body text-xs text-slate">
          {item.present ? `${item.score_percent}%` : "not found"}
        </span>
      </div>
      <div
        className="relative h-2 w-full overflow-hidden rounded-sm bg-line"
        role="progressbar"
        aria-valuenow={item.score_percent}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label={item.name}
      >
        <div
          className={`h-full rounded-sm ${
            item.present ? "bg-brass" : "bg-transparent"
          }`}
          style={{ width: `${item.score_percent}%` }}
        />
      </div>
    </div>
  );
}
