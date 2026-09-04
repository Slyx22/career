"""
Canonical skill taxonomy.

This is the single source of truth for skill names used across the
application. The frontend never hard-codes skill names - it renders
whatever the Python engine returns.

Each skill entry has:
- canonical: the display name
- slug: a stable identifier (used in the DB and career models)
- category: grouping used for the skill-breakdown UI
- aliases: alternate phrasings that should be recognized in CV text

NOTE: The taxonomy originally covered only "ML Engineer" for Phase 1. It
has since grown to support Data Scientist, Software Engineer, and
English Teacher, and the structure supports adding more careers/skills
later without code changes to the extraction or scoring engine.
"""
from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class Skill:
    slug: str
    canonical: str
    category: str
    aliases: List[str] = field(default_factory=list)


SKILL_TAXONOMY: List[Skill] = [
    # Programming
    Skill("python", "Python", "Programming", ["python programming", "python 3", "python development", "py"]),
    Skill("sql", "SQL", "Programming", ["structured query language", "sql queries"]),
    Skill("git", "Git", "Programming", ["version control", "github", "gitlab"]),
    Skill("bash", "Bash", "Programming", ["shell scripting", "shell script", "unix shell"]),

    # Data
    Skill("numpy", "NumPy", "Data", ["numpy arrays"]),
    Skill("pandas", "Pandas", "Data", ["pandas dataframe", "pandas dataframes"]),
    Skill("data_preprocessing", "Data preprocessing", "Data", ["data cleaning", "data wrangling", "feature preprocessing"]),
    Skill("data_pipelines", "Data pipelines", "Data", ["etl pipeline", "etl pipelines", "data pipeline"]),

    # Machine Learning
    Skill("machine_learning", "Machine learning", "Machine Learning", ["ml", "machine-learning", "applied machine learning"]),
    Skill("supervised_learning", "Supervised learning", "Machine Learning", ["classification models", "regression models"]),
    Skill("unsupervised_learning", "Unsupervised learning", "Machine Learning", ["clustering", "dimensionality reduction"]),
    Skill("model_evaluation", "Model evaluation", "Machine Learning", ["cross validation", "cross-validation", "model validation"]),
    Skill("feature_engineering", "Feature engineering", "Machine Learning", ["feature selection", "feature extraction"]),
    Skill("scikit_learn", "scikit-learn", "Machine Learning", ["sklearn", "scikit learn"]),

    # Deep Learning
    Skill("pytorch", "PyTorch", "Deep Learning", ["torch"]),
    Skill("tensorflow", "TensorFlow", "Deep Learning", ["tf", "keras"]),
    Skill("neural_networks", "Neural networks", "Deep Learning", ["cnn", "rnn", "transformer", "transformers", "neural network"]),
    Skill("deep_learning", "Deep learning", "Deep Learning", ["dl"]),

    # Deployment
    Skill("docker", "Docker", "Deployment", ["containerization", "containerisation", "dockerized", "dockerised"]),
    Skill("fastapi", "FastAPI", "Deployment", ["fast api"]),
    Skill("rest_apis", "REST APIs", "Deployment", ["restful api", "restful apis", "rest api"]),
    Skill("kubernetes", "Kubernetes", "Deployment", ["k8s"]),

    # Cloud
    Skill("aws", "AWS", "Cloud", ["amazon web services", "aws cloud", "sagemaker", "amazon sagemaker"]),
    Skill("gcp", "GCP", "Cloud", ["google cloud platform", "google cloud", "vertex ai"]),
    Skill("azure", "Azure", "Cloud", ["microsoft azure", "azure ml", "azure machine learning"]),

    # MLOps
    Skill("cicd", "CI/CD", "MLOps", ["continuous integration", "continuous deployment", "ci/cd pipeline", "github actions"]),
    Skill("mlflow", "MLflow", "MLOps", ["ml flow"]),
    Skill("model_monitoring", "Model monitoring", "MLOps", ["monitoring models in production", "drift detection"]),
    Skill("experiment_tracking", "Experiment tracking", "MLOps", ["experiment management"]),
    Skill("model_deployment", "Model deployment", "MLOps", ["deploying models", "deployed a model", "model serving"]),

    # Databases
    Skill("postgresql", "PostgreSQL", "Databases", ["postgres"]),
    Skill("mysql", "MySQL", "Databases", []),
    Skill("mongodb", "MongoDB", "Databases", ["mongo"]),

    # Statistics
    Skill("statistics", "Statistics", "Statistics", ["statistical analysis", "statistical methods"]),
    Skill("probability", "Probability", "Statistics", ["probability theory"]),
    Skill("hypothesis_testing", "Hypothesis testing", "Statistics", ["a/b testing", "ab testing", "statistical testing"]),
    Skill("data_visualization", "Data visualization", "Statistics", ["matplotlib", "seaborn", "tableau", "power bi", "data viz"]),

    # Software Engineering (general, non-ML software roles)
    Skill("java", "Java", "Software Engineering", ["java programming", "java development"]),
    Skill("javascript", "JavaScript", "Software Engineering", ["js", "es6", "ecmascript"]),
    Skill("typescript", "TypeScript", "Software Engineering", ["ts"]),
    Skill("data_structures_algorithms", "Data structures & algorithms", "Software Engineering", ["dsa", "algorithms", "data structures"]),
    Skill("system_design", "System design", "Software Engineering", ["distributed systems design", "architecture design", "scalable systems"]),
    Skill("object_oriented_design", "Object-oriented design", "Software Engineering", ["oop", "object oriented programming", "object-oriented programming"]),
    Skill("unit_testing", "Unit testing", "Software Engineering", ["test driven development", "tdd", "automated testing"]),
    Skill("agile_scrum", "Agile / Scrum", "Software Engineering", ["agile methodology", "scrum", "sprint planning"]),

    # Education / Teaching
    Skill("lesson_planning", "Lesson planning", "Education", ["lesson plans", "unit planning", "curriculum planning"]),
    Skill("classroom_management", "Classroom management", "Education", ["behavior management", "classroom discipline"]),
    Skill("curriculum_development", "Curriculum development", "Education", ["curriculum design", "syllabus design"]),
    Skill("differentiated_instruction", "Differentiated instruction", "Education", ["differentiated learning", "individualized instruction"]),
    Skill("literacy_instruction", "Literacy instruction", "Education", ["reading instruction", "reading comprehension instruction"]),
    Skill("assessment_design", "Student assessment", "Education", ["grading", "rubric design", "formative assessment", "summative assessment"]),
    Skill("educational_technology", "Educational technology", "Education", ["edtech", "google classroom", "learning management system", "lms"]),
    Skill("parent_communication", "Parent communication", "Education", ["parent-teacher conferences", "parent teacher communication"]),
    Skill("esl_instruction", "ESL / ELL instruction", "Education", ["english as a second language", "english language learners", "tesol"]),
    Skill("special_needs_accommodation", "Special needs accommodation", "Education", ["iep", "individualized education plan", "inclusive education"]),
    Skill("grammar_composition", "Grammar & composition instruction", "Education", ["grammar instruction", "writing instruction", "composition"]),
    Skill("literature_analysis", "Literary analysis instruction", "Education", ["teaching literature", "literary criticism"]),
    Skill("public_speaking", "Public speaking", "Education", ["presentation skills", "oral communication"]),
]

SKILL_BY_SLUG = {s.slug: s for s in SKILL_TAXONOMY}


def all_categories() -> List[str]:
    seen = []
    for s in SKILL_TAXONOMY:
        if s.category not in seen:
            seen.append(s.category)
    return seen
