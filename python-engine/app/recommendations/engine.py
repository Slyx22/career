"""
Recommendation generation.

Turns the ranked skill gaps into 3-5 concrete next actions. This is
template-based and fully deterministic by default (no AI API required).
If AI_API_KEY is configured, the caller may optionally pass the
templated recommendations through an LLM purely to rephrase them more
naturally - the *content/priority* still comes from this engine, per
build spec section 27 (the LLM never decides the score or the gap list).
"""
from __future__ import annotations

from typing import List

from app.nlp.onet_elements import ACTION_BY_SLUG
from app.scoring.scorer import SkillScoreDetail

_ACTION_TEMPLATES = {
    "docker": "Package one of your projects with Docker and write down how to build and run it.",
    "kubernetes": "Deploy a small containerised app to a free local Kubernetes cluster (e.g. minikube) and document it.",
    "aws": "Use the AWS free tier to host a small project, then add it to your CV.",
    "gcp": "Use Google Cloud's free tier to host a small project, then add it to your CV.",
    "azure": "Use Microsoft Azure's free tier (or Microsoft Learn sandbox) for a small project, then add it to your CV.",
    "model_deployment": "Take one of your models end-to-end: wrap it behind a REST API and deploy it.",
    "fastapi": "Build a small FastAPI service and put the code on GitHub.",
    "cicd": "Set up automatic tests and deployment (e.g. GitHub Actions) for one of your projects.",
    "mlflow": "Track experiments for one project using MLflow (or a similar tool).",
    "model_monitoring": "Add basic monitoring/logging to a deployed model to track prediction drift.",
    "experiment_tracking": "Log metrics and parameters for your model experiments using a tracking tool.",
    "pytorch": "Build and train a small neural network with PyTorch and document the results.",
    "tensorflow": "Build and train a small model with TensorFlow/Keras and document the results.",
    "deep_learning": "Complete a deep-learning project (e.g. an image or text classifier) and document results.",
    "scikit_learn": "Use scikit-learn to build and evaluate a model on a public dataset.",
    "feature_engineering": "Practice feature engineering on a public dataset and document the impact on model performance.",
    "model_evaluation": "Add proper evaluation (cross-validation, relevant metrics) to a past project.",
    "data_pipelines": "Build a small pipeline that automatically moves and cleans data, and document it.",
    "sql": "Practise SQL on a free dataset (e.g. SQLite or PostgreSQL) and add a short project to your CV.",
    "statistics": "Strengthen your statistics (averages, distributions, significance) and show it in a small analysis.",
    "postgresql": "Set up and query a PostgreSQL database as part of a project.",
    "microsoft_excel": "Do a free Excel course (formulas, pivot tables, VLOOKUP) and list what you can do under Skills.",
    "microsoft_office": "List the Microsoft Office programs you can use (Word, Excel, PowerPoint, Outlook) under Skills.",
}

_GENERIC_TEMPLATE = "Build a small project that specifically demonstrates {skill}."
_TOOL_TEMPLATE = (
    "Learn the basics of {skill} with a free course or trial version, then add it to your CV "
    "with one sentence on what you used it for."
)
_TOOL_CATEGORIES = {"Workplace software", "Cloud", "Databases", "Deployment", "MLOps"}


_TOOL_SOURCE = "onet_technology_skills"


def action_for(detail: SkillScoreDetail) -> str:
    """One concrete step to show or build a single skill."""
    template = _ACTION_TEMPLATES.get(detail.slug) or ACTION_BY_SLUG.get(detail.slug)
    if template:
        return template
    is_tool = getattr(detail, "is_tool", False) or detail.category in _TOOL_CATEGORIES
    return (_TOOL_TEMPLATE if is_tool else _GENERIC_TEMPLATE).format(skill=detail.name)


def generate_recommendations(gap_details: List[SkillScoreDetail], limit: int = 5) -> List[str]:
    recommendations: List[str] = []
    for detail in gap_details:
        step = action_for(detail)
        if step not in recommendations:
            recommendations.append(step)
        if len(recommendations) >= limit:
            break
    if not recommendations:
        recommendations.append(
            "Great coverage of the skills this career needs - consider deepening "
            "your strongest areas with a portfolio project that shows end-to-end ownership."
        )

    return recommendations[:limit] if len(recommendations) >= 3 else recommendations
