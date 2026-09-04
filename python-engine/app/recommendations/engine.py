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

from app.scoring.scorer import SkillScoreDetail

_ACTION_TEMPLATES = {
    "docker": "Containerize a small project with Docker and document the build/run steps.",
    "kubernetes": "Deploy a containerized service to a local Kubernetes cluster (e.g. via minikube).",
    "aws": "Deploy a trained model behind an API on AWS (e.g. EC2, Lambda, or SageMaker).",
    "gcp": "Deploy a model or pipeline using a core GCP service (e.g. Vertex AI or Cloud Run).",
    "azure": "Deploy a model using Azure Machine Learning or an Azure-hosted API.",
    "model_deployment": "Take one of your models end-to-end: wrap it behind a REST API and deploy it.",
    "fastapi": "Build a small FastAPI service that serves predictions from one of your models.",
    "cicd": "Set up a CI/CD pipeline (e.g. GitHub Actions) that tests and deploys a project automatically.",
    "mlflow": "Track experiments for one project using MLflow (or a similar experiment tracker).",
    "model_monitoring": "Add basic monitoring/logging to a deployed model to track prediction drift.",
    "experiment_tracking": "Log metrics and parameters for your model experiments using a tracking tool.",
    "pytorch": "Build and train a neural network from scratch using PyTorch.",
    "tensorflow": "Build and train a model using TensorFlow/Keras end-to-end.",
    "deep_learning": "Complete a deep-learning project (e.g. an image or text classifier) and document results.",
    "scikit_learn": "Use scikit-learn to build and evaluate a supervised learning pipeline on a real dataset.",
    "feature_engineering": "Practice feature engineering on a public dataset and document the impact on model performance.",
    "model_evaluation": "Add rigorous evaluation (cross-validation, relevant metrics) to a past ML project.",
    "data_pipelines": "Build a small ETL/data pipeline that moves and transforms data automatically.",
    "sql": "Practice writing SQL queries against a real relational dataset.",
    "statistics": "Strengthen statistics fundamentals relevant to ML (distributions, significance testing).",
    "postgresql": "Set up and query a PostgreSQL database as part of a project.",
}

_GENERIC_TEMPLATE = "Build a small project that specifically demonstrates {skill}."


def generate_recommendations(gap_details: List[SkillScoreDetail], limit: int = 5) -> List[str]:
    recommendations: List[str] = []
    for detail in gap_details[:limit]:
        template = _ACTION_TEMPLATES.get(detail.slug)
        recommendations.append(template or _GENERIC_TEMPLATE.format(skill=detail.name))

    if not recommendations:
        recommendations.append(
            "Great coverage across the core ML Engineer skill set - consider deepening "
            "your strongest areas with a portfolio project that showcases end-to-end ownership."
        )

    return recommendations[:limit] if len(recommendations) >= 3 else recommendations
