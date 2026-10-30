"""
Recommendation generation.

Turns the CV checks and the ranked skill gaps into 3-5 next steps. Every
step is something the person can add to or reword on their CV today:
never "build a project", "take a course" or "show work samples". Each
skill step says why it matters (how important the skill is for this
occupation, from O*NET).

Fully rule-based and deterministic: no AI API is needed or used. (If
AI_API_KEY is configured, the caller may still pass the text through an
LLM purely to rephrase it; the content and order always come from here.)
"""
from __future__ import annotations

from typing import List, Optional

from app.nlp.onet_elements import ACTION_BY_SLUG
from app.scoring.scorer import SkillScoreDetail

# Skills from the original hand-built tech careers whose steps need more
# than the generic tool line.
_ACTION_TEMPLATES = {
    "microsoft_excel": "List Excel under Skills with what you can do in it (e.g. formulas, pivot tables, VLOOKUP).",
    "microsoft_office": "List the Microsoft Office programs you can use (Word, Excel, PowerPoint, Outlook) under Skills.",
    "sql": "If you've written SQL queries, list SQL under Skills and name it in the job or project where you used it.",
    "statistics": "Add any statistics subjects under Education, and mention statistical work in the job or project where you did it.",
}

_GENERIC_TEMPLATE = (
    "If you have experience with {skill}, add it to the job, studies or project where you used it, "
    "and list it under Skills."
)
_TOOL_TEMPLATE = "If you've used {skill}, list it under Skills and name it in the job or project where you used it."
_TOOL_CATEGORIES = {"Workplace software", "Cloud", "Databases", "Deployment", "MLOps"}

_WHY = {
    "essential": "very important for this job",
    "important": "important for this job",
    "useful": "useful for this job",
}


def why_it_matters(detail: SkillScoreDetail) -> Optional[str]:
    """Plain-words importance of a skill for the occupation (from O*NET)."""
    return _WHY.get(getattr(detail, "importance_level", "") or "")


def action_for(detail: SkillScoreDetail) -> str:
    """What to add to the CV to show one skill."""
    template = _ACTION_TEMPLATES.get(detail.slug) or ACTION_BY_SLUG.get(detail.slug)
    if template:
        return template
    is_tool = getattr(detail, "is_tool", False) or detail.category in _TOOL_CATEGORIES
    return (_TOOL_TEMPLATE if is_tool else _GENERIC_TEMPLATE).format(skill=detail.name)


def skill_step(detail: SkillScoreDetail) -> str:
    why = why_it_matters(detail)
    head = f"{detail.name} ({why})" if why else detail.name
    return f"{head}: {action_for(detail)}"


def generate_recommendations(
    gap_details: List[SkillScoreDetail],
    limit: int = 5,
    first_steps: Optional[List[str]] = None,
) -> List[str]:
    """`first_steps` are CV checks (required registrations, weak lines,
    missing sections) that come before skill gaps."""
    recommendations: List[str] = []
    for step in first_steps or []:
        if step and step not in recommendations:
            recommendations.append(step)
        if len(recommendations) >= 2:  # leave room for the skills this job needs
            break
    seen_actions = set()
    for detail in gap_details:
        if len(recommendations) >= limit:
            break
        action = action_for(detail)
        if action in seen_actions:
            continue
        seen_actions.add(action)
        recommendations.append(skill_step(detail))
    if not recommendations:
        recommendations.append(
            "Your CV already shows the skills this career needs. Keep each job entry specific: "
            "what you did, and a number or result where you can."
        )
    return recommendations[:limit]
