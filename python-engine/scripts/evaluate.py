"""
CV evaluation benchmark: does the scoring point in the right direction?

Uses the hand-written South African test CVs in tests/benchmark/ (a strong
and a weak CV for each of 10 common jobs) and checks three things:

  1. Right job first  - a strong CV scores highest for its own job, out of
                        the 10 jobs in the benchmark.
  2. Strong beats weak - for the same job, the strong CV scores clearly
                        higher than the weak one.
  3. Evidence helps   - adding one clear line of evidence for the biggest
                        gap raises the score (never lowers it).

Run:  python scripts/evaluate.py          (prints a report)
The same checks run as tests in tests/test_benchmark.py.
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.extractors.cv_extractor import extract_from_text  # noqa: E402
from app.nlp.skill_extractor import extract_skill_evidence  # noqa: E402
from app.scoring.career_model import get_career_model  # noqa: E402
from app.scoring.scorer import score_career_readiness  # noqa: E402

BENCH = ROOT / "tests" / "benchmark"
STRONG_MARGIN = 15  # strong CV must beat weak CV by at least this many points

# One clear sentence of evidence per skill, used for the "evidence helps" check.
EVIDENCE_LINES = {
    "default": "Experience: I led a project where I {skill} for a team and delivered measurable results in 2026.",
}


def score_text(text: str, career_slug: str):
    cv = extract_from_text(text)
    evidence = extract_skill_evidence(cv)
    return score_career_readiness(evidence, get_career_model(career_slug), cv_text=cv.raw_text)


@dataclass
class JobResult:
    job: str
    career: str
    strong: int
    weak: int
    rank_of_own_career: int
    top_career: str
    scores_by_career: Dict[str, int] = field(default_factory=dict)
    evidence_before: int = 0
    evidence_after: int = 0
    evidence_skill: str = ""

    @property
    def right_job_first(self) -> bool:
        return self.rank_of_own_career == 1

    @property
    def strong_beats_weak(self) -> bool:
        return self.strong - self.weak >= STRONG_MARGIN

    @property
    def evidence_helps(self) -> bool:
        return self.evidence_after > self.evidence_before


def run() -> List[JobResult]:
    cases = json.loads((BENCH / "cases.json").read_text())
    comparison = cases["comparison_careers"]
    results = []
    for job in cases["jobs"]:
        strong_text = (BENCH / "cvs" / f"{job['id']}_strong.txt").read_text()
        weak_text = (BENCH / "cvs" / f"{job['id']}_weak.txt").read_text()

        scores = {c: score_text(strong_text, c).overall_score for c in comparison}
        ranked = sorted(scores, key=lambda c: scores[c], reverse=True)
        own = job["career"]

        weak_result = score_text(weak_text, own)
        # Evidence check on the weak CV: add one line for its biggest gap.
        gap = (weak_result.gap_details or [None])[0]
        skill_name = gap.name.lower() if gap else "worked"
        added = weak_text + "\n" + EVIDENCE_LINES["default"].format(skill=f"used {skill_name}")
        after = score_text(added, own).overall_score

        results.append(
            JobResult(
                job=job["id"],
                career=own,
                strong=scores[own],
                weak=weak_result.overall_score,
                rank_of_own_career=ranked.index(own) + 1,
                top_career=ranked[0],
                scores_by_career=scores,
                evidence_before=weak_result.overall_score,
                evidence_after=after,
                evidence_skill=gap.name if gap else "",
            )
        )
    return results


def main():
    results = run()
    print(f"{'Job':15} {'Strong':>6} {'Weak':>5} {'Own rank':>9}  {'Evidence':>9}  Highest-scoring job (if not own)")
    for r in results:
        flag = "" if r.right_job_first else f"{r.top_career} ({r.scores_by_career[r.top_career]})"
        print(
            f"{r.job:15} {r.strong:>6} {r.weak:>5} {r.rank_of_own_career:>6}/10  "
            f"{r.evidence_before:>3}->{r.evidence_after:<4} {flag}"
        )
    n = len(results)
    print()
    print(f"Right job first:   {sum(r.right_job_first for r in results)}/{n}")
    print(f"Strong beats weak: {sum(r.strong_beats_weak for r in results)}/{n} (by {STRONG_MARGIN}+ points)")
    print(f"Evidence helps:    {sum(r.evidence_helps for r in results)}/{n}")


if __name__ == "__main__":
    main()
