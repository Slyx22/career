# Evaluation: is the score pointing in the right direction?

Organisations will only pay for candidates if a high score really means
a stronger candidate. This is the plan to make sure it does, from what
runs today to what we prove later.

## Level 1: Benchmark (running now)

`python-engine/tests/benchmark/` holds 20 realistic South African CVs: a
strong and a weak CV for 10 common jobs (accounts clerk, nurse, software
developer, electrician, foundation phase teacher, call centre agent,
retail sales, security officer, truck driver, chef).

Every change to scoring, skills or career data must pass, in CI:

| Check | Rule | Today |
|---|---|---|
| Right job first | A strong CV scores highest for its own job out of the 10 | 10/10 |
| Strong beats weak | Strong CV beats weak CV by 15+ points; strong ≥ 55, weak ≤ 30 | 10/10 |
| Evidence helps | Adding one clear line for the biggest gap raises the score | 10/10 |

Run `python scripts/evaluate.py` for the report.

**What it found and fixed (October 2026):** experienced candidates scored
too low (a security officer with 5 years and PSIRA Grade B scored 32),
because the app didn't recognise ordinary achievement wording
("patrolled", "processed payroll for 120 employees") or common CV phrases
("trained new guards", "wrote incident reports"). A nurse CV also scored
higher for Security Guard than for Nurse. After the fix, strong CVs score
57–78 and every CV's own job ranks first. Certificates from then on say
method 2.2.

**Limits:** 20 CVs written by us. It catches big mistakes, not subtle bias.

### Growing the benchmark
- Add a job whenever users pick it often (check `analyses` by career).
- Add "tricky" CVs: career changers, CVs in bullet fragments, CVs
  mentioning isiZulu/Afrikaans terms, matric-only CVs, CVs with gaps.
- Never use a real person's CV in the repo. Write or fully anonymise.

## Level 2: User feedback (next)

After results, ask one optional question: "Does this score feel right for
where you are?" (too high / about right / too low) and store it with the
analysis (consent covered by the privacy policy update that ships with it).
Target: "about right" ≥ 60%; investigate any job where "too high" > 25%.

## Level 3: Recruiter grading study

1. Collect 200 CVs with explicit consent for research, fully anonymised.
2. Two or three recruiters / HR practitioners grade each one for a job
   (1–5, "would you interview?") without seeing our score.
3. Compare. Targets: rank correlation (Spearman) ≥ 0.6 with the average
   recruiter grade; among CVs we score 70+, recruiters would interview
   ≥ 70%; among CVs below 50, ≤ 25%.
4. Partners who could supply graders free: university career offices,
   TVET placement officers, Harambee, SETAs, HR students.

## Level 4: Outcomes

With consent, follow up 3 and 6 months after a certificate: interview?
job? Report the hire rate for 70+ vs below 70. This is the evidence that
makes the certificate genuinely "recognised" (see recognition.md).

## Fairness checks (from Level 3 onwards)

The score must not quietly favour advantaged candidates. For each study,
compare score distributions (at the same recruiter grade) by:
- province and urban/rural, school quintile where known
- home language, gender
Gaps larger than 5 points at the same recruiter grade get investigated
and fixed. Never use race, gender, age or disability as scoring inputs
(and never as employer filters: see employer-platform.md).

## Versioning

Any change that moves scores bumps `METHOD_VERSION` in
`app/services/certificate_service.py`. Certificates show their version,
so old and new results can always be told apart.
