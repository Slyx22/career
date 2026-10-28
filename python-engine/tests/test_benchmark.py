"""
Evaluation benchmark: scoring must point in the right direction.

Hand-written South African CVs (strong and weak for 10 common jobs) live in
tests/benchmark/. Any change to scoring, skills or career data must keep
these checks passing. Run `python scripts/evaluate.py` for the full report.
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import evaluate  # noqa: E402

RESULTS = {r.job: r for r in evaluate.run()}

# A genuinely strong, experienced CV should land in the upper half.
MIN_STRONG_SCORE = 55
# A thin CV with almost no evidence should not look employable.
MAX_WEAK_SCORE = 30


@pytest.mark.parametrize("job", sorted(RESULTS))
def test_right_job_scores_highest(job):
    r = RESULTS[job]
    assert r.right_job_first, f"{job}: own job ranked {r.rank_of_own_career}, top was {r.top_career}"


@pytest.mark.parametrize("job", sorted(RESULTS))
def test_strong_cv_beats_weak_cv(job):
    r = RESULTS[job]
    assert r.strong_beats_weak, f"{job}: strong {r.strong} vs weak {r.weak}"
    assert r.strong >= MIN_STRONG_SCORE, f"{job}: strong CV only scored {r.strong}"
    assert r.weak <= MAX_WEAK_SCORE, f"{job}: weak CV scored {r.weak}"


@pytest.mark.parametrize("job", sorted(RESULTS))
def test_adding_evidence_raises_score(job):
    r = RESULTS[job]
    assert r.evidence_helps, f"{job}: adding evidence for {r.evidence_skill} went {r.evidence_before}->{r.evidence_after}"
