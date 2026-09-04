STRONG_ML_ENGINEER_CV = """
Jane Doe
Machine Learning Engineer

SUMMARY
Machine learning engineer with 5 years of experience building and deploying
production ML systems.

EXPERIENCE
Senior ML Engineer, Acme AI (2022 - 2026)
- Built and deployed a production ML inference API using Python and FastAPI,
  serving predictions to 2M users.
- Designed and trained deep learning models using PyTorch and TensorFlow for
  computer vision tasks.
- Containerized services with Docker and deployed them on Kubernetes and AWS.
- Implemented CI/CD pipelines using GitHub Actions and tracked experiments
  with MLflow.
- Built data pipelines with Pandas and NumPy, and used SQL extensively
  against a PostgreSQL database.
- Led model monitoring efforts to detect and respond to data drift in
  production.

ML Engineer, DataCo (2019 - 2022)
- Developed supervised learning and unsupervised learning models using
  scikit-learn.
- Performed feature engineering and model evaluation using cross-validation.

EDUCATION
BSc Computer Science, 2019

SKILLS
Python, SQL, Git, Bash, Docker, Kubernetes, AWS, GCP, PyTorch, TensorFlow,
scikit-learn, MLflow, FastAPI, PostgreSQL, Statistics, Probability
"""

BEGINNER_CV = """
John Smith

SUMMARY
Recent computer science graduate with an interest in machine learning.

EDUCATION
BSc Computer Science, 2026
University project: built a basic ML model in Python using a university
tutorial as coursework.

SKILLS
Python, basic ML, Git
"""

DATA_SCIENTIST_TRANSITION_CV = """
Alex Chen
Data Scientist

EXPERIENCE
Data Scientist, InsightCorp (2021 - 2026)
- Built and deployed predictive models using Python, Pandas, and scikit-learn.
- Wrote complex SQL queries against PostgreSQL to extract and analyze data.
- Applied statistics and hypothesis testing to evaluate experiment results.
- Performed feature engineering and model evaluation for churn prediction.

PROJECTS
- Personal project: trained a neural network with PyTorch for image
  classification.

SKILLS
Python, SQL, Pandas, scikit-learn, Statistics, Git
"""

EMPTY_CV = "   \n\n  "

# --- "Messy", closer-to-real-world CVs used for robustness testing ---------

# Resume with no terminal punctuation on bullets (common when CVs are
# exported from design tools / bullet lists), to check the extractor
# doesn't crash and still falls back sensibly without sentence boundaries.
NO_PUNCTUATION_BULLET_CV = """
Priya Nair
ML Engineer

EXPERIENCE
Machine Learning Engineer, Northwind Labs 2024 - 2026
Built and deployed a fraud detection model using Python and scikit-learn
Containerized the service with Docker and shipped it to production on AWS
Wrote SQL queries against a PostgreSQL warehouse for feature extraction

SKILLS
Python SQL Docker AWS scikit-learn Git
"""

# Deliberately mixes a strong-evidence sentence immediately next to an
# unrelated weak-evidence sentence, to guard against evidence bleeding
# across sentence boundaries (see test_depth_not_leaked_across_sentence_boundary).
MIXED_SIGNALS_CV = """
Sam Rivera
Junior Developer transitioning into ML

EXPERIENCE
Junior Developer, Small Startup (2023 - 2026)
- Built and shipped several production web features using Python and Git.
- Also somewhat familiar with TensorFlow from a weekend tutorial.
- Basic knowledge of Kubernetes from reading documentation, never used it hands-on.
- Delivered a REST API used by internal tools.

EDUCATION
BSc Information Systems, 2023
"""

# A genuine career changer: strong non-ML technical background, almost no
# ML-specific evidence. Useful for checking the score lands low without
# crashing or producing nonsensical (negative / >100) values.
CAREER_CHANGER_CV = """
Morgan Lee
Backend Developer

SUMMARY
Backend developer with 6 years of experience building web services. New to
machine learning and currently studying it in my spare time.

EXPERIENCE
Backend Developer, Retail Systems Inc (2018 - 2026)
- Built and maintained REST APIs in Python and Java.
- Managed PostgreSQL and MySQL databases for high-traffic e-commerce sites.
- Used Git and CI/CD pipelines for deployment automation.

EDUCATION
BSc Software Engineering, 2018

SKILLS
Python, Java, PostgreSQL, MySQL, Git, CI/CD
"""

# A CV with odd/inconsistent capitalization and spacing, to check the
# case-insensitive matching and whitespace handling hold up.
ODD_FORMATTING_CV = """
ALEX   KIM


   summary
machine learning engineer with experience in   PYTHON   and   docker.


EXPERIENCE
ml engineer,acme(2023-2026)
-built AND deployed models using pytorch and Docker.
-used   aws   for model deployment.

skills
python,pytorch,docker,aws,git
"""

