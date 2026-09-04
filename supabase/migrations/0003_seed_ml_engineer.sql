-- Seed data mirroring the Phase 1 in-code taxonomy
-- (python-engine/app/nlp/taxonomy.py) and career model
-- (python-engine/app/scoring/career_model.py).
--
-- This lets a future Supabase-backed store read the same data the local
-- SQLite/in-code version uses today. Until app/db/supabase_store.py is
-- implemented and STORAGE_BACKEND=supabase is set, the Python engine
-- keeps using its in-code taxonomy/career model directly and this table
-- data is unused - it's provided for forward compatibility only.

insert into careers (name, slug, description) values
    ('ML Engineer', 'ml-engineer',
     'Builds, trains, deploys and maintains machine learning systems in production, spanning data preparation, modeling, and MLOps.')
on conflict (slug) do nothing;

insert into skills (name, slug, category, aliases) values
    ('Python', 'python', 'Programming', array['python programming','python 3','python development','py']),
    ('SQL', 'sql', 'Programming', array['structured query language','sql queries']),
    ('Git', 'git', 'Programming', array['version control','github','gitlab']),
    ('Bash', 'bash', 'Programming', array['shell scripting','shell script','unix shell']),
    ('NumPy', 'numpy', 'Data', array['numpy arrays']),
    ('Pandas', 'pandas', 'Data', array['pandas dataframe','pandas dataframes']),
    ('Data preprocessing', 'data_preprocessing', 'Data', array['data cleaning','data wrangling','feature preprocessing']),
    ('Data pipelines', 'data_pipelines', 'Data', array['etl pipeline','etl pipelines','data pipeline']),
    ('Machine learning', 'machine_learning', 'Machine Learning', array['ml','machine-learning','applied machine learning']),
    ('Supervised learning', 'supervised_learning', 'Machine Learning', array['classification models','regression models']),
    ('Unsupervised learning', 'unsupervised_learning', 'Machine Learning', array['clustering','dimensionality reduction']),
    ('Model evaluation', 'model_evaluation', 'Machine Learning', array['cross validation','cross-validation','model validation']),
    ('Feature engineering', 'feature_engineering', 'Machine Learning', array['feature selection','feature extraction']),
    ('scikit-learn', 'scikit_learn', 'Machine Learning', array['sklearn','scikit learn']),
    ('PyTorch', 'pytorch', 'Deep Learning', array['torch']),
    ('TensorFlow', 'tensorflow', 'Deep Learning', array['tf','keras']),
    ('Neural networks', 'neural_networks', 'Deep Learning', array['cnn','rnn','transformer','transformers','neural network']),
    ('Deep learning', 'deep_learning', 'Deep Learning', array['dl']),
    ('Docker', 'docker', 'Deployment', array['containerization','containerisation','dockerized','dockerised']),
    ('FastAPI', 'fastapi', 'Deployment', array['fast api']),
    ('REST APIs', 'rest_apis', 'Deployment', array['restful api','restful apis','rest api']),
    ('Kubernetes', 'kubernetes', 'Deployment', array['k8s']),
    ('AWS', 'aws', 'Cloud', array['amazon web services','aws cloud','sagemaker','amazon sagemaker']),
    ('GCP', 'gcp', 'Cloud', array['google cloud platform','google cloud','vertex ai']),
    ('Azure', 'azure', 'Cloud', array['microsoft azure','azure ml','azure machine learning']),
    ('CI/CD', 'cicd', 'MLOps', array['continuous integration','continuous deployment','ci/cd pipeline','github actions']),
    ('MLflow', 'mlflow', 'MLOps', array['ml flow']),
    ('Model monitoring', 'model_monitoring', 'MLOps', array['monitoring models in production','drift detection']),
    ('Experiment tracking', 'experiment_tracking', 'MLOps', array['experiment management']),
    ('Model deployment', 'model_deployment', 'MLOps', array['deploying models','deployed a model','model serving']),
    ('PostgreSQL', 'postgresql', 'Databases', array['postgres']),
    ('MySQL', 'mysql', 'Databases', array[]::text[]),
    ('MongoDB', 'mongodb', 'Databases', array['mongo']),
    ('Statistics', 'statistics', 'Statistics', array['statistical analysis','statistical methods']),
    ('Probability', 'probability', 'Statistics', array['probability theory']),
    ('Hypothesis testing', 'hypothesis_testing', 'Statistics', array['a/b testing','ab testing','statistical testing'])
on conflict (slug) do nothing;

-- ML Engineer career model weights.
-- NOTE: market_frequency / market_importance are INITIAL BENCHMARK DATA
-- (is_benchmark_data = true), not verified live job-market statistics.
-- Regenerate this table from a real job-postings dataset before
-- presenting these numbers as verified market data.
insert into career_skills (career_id, skill_id, market_frequency, market_importance, is_benchmark_data)
select c.id, s.id, v.market_frequency, v.market_importance, true
from (values
    ('python', 0.91, 1.00), ('sql', 0.62, 0.60), ('git', 0.70, 0.55), ('bash', 0.35, 0.35),
    ('numpy', 0.68, 0.65), ('pandas', 0.72, 0.70), ('data_preprocessing', 0.75, 0.80), ('data_pipelines', 0.55, 0.75),
    ('machine_learning', 0.95, 1.00), ('supervised_learning', 0.58, 0.70), ('unsupervised_learning', 0.30, 0.45),
    ('model_evaluation', 0.60, 0.75), ('feature_engineering', 0.50, 0.70), ('scikit_learn', 0.60, 0.65),
    ('pytorch', 0.55, 0.80), ('tensorflow', 0.45, 0.70), ('neural_networks', 0.50, 0.75), ('deep_learning', 0.52, 0.80),
    ('docker', 0.58, 0.85), ('fastapi', 0.25, 0.55), ('rest_apis', 0.40, 0.60), ('kubernetes', 0.29, 0.55),
    ('aws', 0.48, 0.75), ('gcp', 0.25, 0.55), ('azure', 0.20, 0.50),
    ('cicd', 0.35, 0.65), ('mlflow', 0.20, 0.55), ('model_monitoring', 0.25, 0.65),
    ('experiment_tracking', 0.22, 0.55), ('model_deployment', 0.45, 0.90),
    ('postgresql', 0.30, 0.40), ('mysql', 0.15, 0.30), ('mongodb', 0.15, 0.30),
    ('statistics', 0.55, 0.70), ('probability', 0.40, 0.55), ('hypothesis_testing', 0.25, 0.45)
) as v(skill_slug, market_frequency, market_importance)
join skills s on s.slug = v.skill_slug
join careers c on c.slug = 'ml-engineer'
on conflict (career_id, skill_id) do nothing;
