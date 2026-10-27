"""
The O*NET Skills and Knowledge elements, mapped one-to-one to skills in
our taxonomy.

Why this file exists: the old importer matched O*NET element names to our
skills with a loose two-way substring test, so "Reading Comprehension"
became "Literacy instruction", and short aliases such as "py" matched
inside words like "therapy". That gave 910 careers the same nine skills
(Python, TypeScript, ESL instruction, ...). This table replaces guessing
with an exact, reviewed mapping keyed by O*NET Element ID.

Each entry:
  element_ids  - O*NET Element IDs (stable across releases)
  onet_names   - O*NET Element Names, used if a release lacks IDs
  slug / name / category - the skill as shown to users
  aliases      - words and phrases that show the skill in a CV
  action       - a concrete next step, used for recommendations

Mathematics appears in both O*NET Skills (2.A.1.e) and Knowledge
(2.C.4.a); both map to one "mathematics" skill so a CV isn't asked to
prove it twice.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass(frozen=True)
class OnetElement:
    element_ids: Tuple[str, ...]
    onet_names: Tuple[str, ...]
    slug: str
    name: str
    category: str
    aliases: Tuple[str, ...]
    action: str


CORE = "Core skills"
PEOPLE = "People skills"
TECH = "Technical skills"
MGMT = "Management"
KNOW = "Knowledge"

ONET_ELEMENTS: List[OnetElement] = [
    # ---------------- O*NET Skills: basic content ----------------
    OnetElement(("2.A.1.a",), ("Reading Comprehension",), "reading_comprehension", "Reading comprehension", CORE,
                ("reading comprehension", "research", "researched", "literature review", "reviewed documents", "reviewing documents", "interpreted", "analysed reports", "analyzed reports", "policy review", "reviewed"),
                "Show reading and interpretation in your CV, e.g. a line on reviewing reports, policies or technical documents and what you did with them."),
    OnetElement(("2.A.1.b",), ("Active Listening",), "active_listening", "Active listening", PEOPLE,
                ("active listening", "listening skills", "customer service", "client liaison", "client relations", "customer queries", "handled queries", "needs assessment", "interviewing", "counselling", "counseling", "communication skills", "listened"),
                "Describe a role where you dealt with customers, clients or colleagues' requests, and the outcome."),
    OnetElement(("2.A.1.c",), ("Writing",), "writing", "Writing", CORE,
                ("writing", "written communication", "report writing", "wrote", "drafted", "documentation", "copywriting", "technical writing", "minutes", "proposals", "content writing", "blog", "reported", "reports", "prepared reports"),
                "Add evidence of writing: reports, proposals, documentation or articles you wrote, with a link if possible."),
    OnetElement(("2.A.1.d",), ("Speaking",), "speaking", "Speaking", PEOPLE,
                ("public speaking", "presentation skills", "presentations", "presented", "verbal communication",
                 "oral communication", "communication skills", "facilitated", "spokesperson", "debating", "debate"),
                "Give a presentation (class, church, community or work) and add it to your CV with the audience size."),
    OnetElement(("2.A.1.e", "2.C.4.a"), ("Mathematics",), "mathematics", "Mathematics", CORE,
                ("mathematics", "maths", "math", "calculus", "algebra", "statistics", "statistical", "quantitative", "numerical", "numeracy", "calculations", "financial modelling", "financial modeling", "mathematical", "reconciliations", "financial statements", "data analysis", "budgeting"),
                "Strengthen and show your maths: list relevant subjects and results, or a project where you worked with numbers."),
    OnetElement(("2.A.1.f",), ("Science",), "science", "Scientific method", CORE,
                ("scientific", "science", "laboratory", "lab work", "experiments", "experimental", "research methodology",
                 "hypothesis", "data collection", "fieldwork"),
                "Add a project or lab work where you tested an idea, collected data and reported the results."),

    # ---------------- O*NET Skills: process ----------------
    OnetElement(("2.A.2.a",), ("Critical Thinking",), "critical_thinking", "Critical thinking", CORE,
                ("critical thinking", "problem solving", "problem-solving", "analytical", "analytical thinking",
                 "analysis", "analysed", "analyzed", "evaluated", "root cause", "assessed"),
                "Add one example of a problem you analysed, the options you weighed and the result."),
    OnetElement(("2.A.2.b",), ("Active Learning",), "active_learning", "Active learning", CORE,
                ("self-taught", "self taught", "quick learner", "fast learner", "upskilled", "certification", "certified",
                 "online course", "coursera", "udemy", "edx", "short course", "continuous learning", "workshop"),
                "Complete a free online course for this career and list it under Certifications with the date."),
    OnetElement(("2.A.2.c",), ("Learning Strategies",), "learning_strategies", "Learning strategies", PEOPLE,
                ("tutoring", "tutor", "mentoring", "mentored", "coaching", "coached", "training others", "trained staff",
                 "lesson planning", "study groups", "curriculum"),
                "Tutor or mentor someone and add it to your CV, including what and how you taught."),
    OnetElement(("2.A.2.d",), ("Monitoring",), "monitoring", "Monitoring performance", CORE,
                ("monitored", "monitoring", "tracked", "tracking", "kpi", "kpis", "performance review", "audit", "audited", "evaluation", "progress reports", "compliance checks", "variances", "vital signs", "reconciliations"),
                "Show how you tracked results or quality, for example KPIs, audits or progress reports you kept."),

    # ---------------- O*NET Skills: social ----------------
    OnetElement(("2.B.1.a",), ("Social Perceptiveness",), "social_perceptiveness", "Social perceptiveness", PEOPLE,
                ("empathy", "empathetic", "interpersonal skills", "interpersonal", "emotional intelligence",
                 "patient care", "community work", "volunteer", "volunteered", "volunteering", "people skills"),
                "Add volunteer or community work that shows you understand and respond to people's needs."),
    OnetElement(("2.B.1.b",), ("Coordination",), "coordination", "Coordination", PEOPLE,
                ("coordinated", "coordination", "coordinator", "teamwork", "team player", "collaborated", "collaboration",
                 "cross-functional", "liaised", "scheduling", "organised events", "organized events", "event planning"),
                "Describe a time you coordinated people or tasks, such as an event, team project or roster."),
    OnetElement(("2.B.1.c",), ("Persuasion",), "persuasion", "Persuasion", PEOPLE,
                ("persuasion", "persuasive", "influenced", "convinced", "pitching", "pitched", "advocacy", "campaign",
                 "sales", "fundraising", "lobbying"),
                "Add an example where you convinced others: a pitch, sale, fundraiser or campaign, with the result."),
    OnetElement(("2.B.1.d",), ("Negotiation",), "negotiation", "Negotiation", PEOPLE,
                ("negotiation", "negotiated", "negotiating", "conflict resolution", "mediation", "mediated",
                 "contract negotiation", "procurement", "dispute resolution"),
                "Add an example of a negotiation or conflict you helped resolve, and what was agreed."),
    OnetElement(("2.B.1.e",), ("Instructing",), "instructing", "Instructing others", PEOPLE,
                ("instructing", "instructed", "teaching", "taught", "trained staff", "trained new", "trained others", "trained employees", "onboarding",
                 "facilitator", "teacher", "lecturer", "tutor"),
                "Teach or train someone in a skill and list it, including how many people you trained."),
    OnetElement(("2.B.1.f",), ("Service Orientation",), "service_orientation", "Service orientation", PEOPLE,
                ("customer service", "client service", "customer care", "service delivery", "helpdesk", "help desk",
                 "front desk", "reception", "hospitality", "call centre", "call center", "customer satisfaction"),
                "Add customer-facing experience (retail, call centre, hospitality, volunteering) and what you improved."),

    # ---------------- O*NET Skills: complex problem solving & technical ----------------
    OnetElement(("2.B.2.i",), ("Complex Problem Solving",), "complex_problem_solving", "Complex problem solving", CORE,
                ("complex problem solving", "problem solving", "problem-solving", "solved", "resolved", "troubleshot",
                 "improved process", "process improvement", "innovation"),
                "Write up one complex problem you solved: the situation, what you did, and the measurable result."),
    OnetElement(("2.B.3.a",), ("Operations Analysis",), "operations_analysis", "Operations analysis", TECH,
                ("requirements gathering", "requirements analysis", "business analysis", "needs analysis",
                 "process mapping", "user requirements", "business requirements", "gap analysis"),
                "Do a small requirements exercise: interview a user, write their needs down and show how a solution meets them."),
    OnetElement(("2.B.3.b",), ("Technology Design",), "technology_design", "Technology design", TECH,
                ("designed", "prototype", "prototyping", "product design", "system design", "solution design",
                 "engineering design", "cad", "user experience", "ux design"),
                "Design and build a small prototype for this field and include photos, drawings or a link."),
    OnetElement(("2.B.3.c",), ("Equipment Selection",), "equipment_selection", "Equipment selection", TECH,
                ("equipment selection", "selected equipment", "specified equipment", "tools selection",
                 "procurement of equipment", "sourcing equipment", "specification"),
                "Show you can choose the right tools or equipment for a job, e.g. a project where you specified what to buy or use."),
    OnetElement(("2.B.3.d",), ("Installation",), "installation", "Installation", TECH,
                ("installation", "installed", "installing", "commissioning", "fitted", "fitting",
                 "wiring", "assembled", "assembly"),
                "Add hands-on installation work (equipment, software, wiring, fittings) with what you installed."),
    OnetElement(("2.B.3.e",), ("Programming",), "programming", "Programming", TECH,
                ("programming", "coding", "software development", "scripting", "developer", "programmer", "github",
                 "python", "java", "javascript", "c++", "c#", "sql", "vba"),
                "Build a small program for a real problem in this field and put the code on GitHub."),
    OnetElement(("2.B.3.g",), ("Operations Monitoring",), "operations_monitoring", "Operations monitoring", TECH,
                ("operations monitoring", "monitored systems", "monitored equipment", "gauges", "readings", "dashboards",
                 "system monitoring", "control room", "inspections", "inspected"),
                "Describe work where you watched gauges, dashboards or equipment to make sure things ran correctly."),
    OnetElement(("2.B.3.h",), ("Operation and Control",), "operation_and_control", "Operating equipment", TECH,
                ("operated", "operating", "operator", "machine operation", "forklift", "driving", "drove",
                 "control systems", "plant operation", "heavy machinery"),
                "List machines, vehicles or systems you have operated, with any licences or certificates."),
    OnetElement(("2.B.3.j",), ("Equipment Maintenance",), "equipment_maintenance", "Equipment maintenance", TECH,
                ("maintenance", "maintained", "preventive maintenance", "servicing", "serviced", "upkeep",
                 "lubrication", "maintenance schedule"),
                "Add maintenance experience: what equipment you looked after and how often."),
    OnetElement(("2.B.3.k",), ("Troubleshooting",), "troubleshooting", "Troubleshooting", TECH,
                ("troubleshooting", "troubleshoot", "troubleshot", "diagnosed", "diagnostics", "fault finding",
                 "fault-finding", "debugging", "debugged", "technical support", "it support"),
                "Add an example of a fault you diagnosed and fixed, and how you found the cause."),
    OnetElement(("2.B.3.l",), ("Repairing",), "repairing", "Repairing", TECH,
                ("repair", "repaired", "repairing", "repairs", "replaced parts", "refurbished", "overhauled",
                 "mechanic", "artisan"),
                "List repair work you have done (machines, vehicles, devices, buildings) and any trade training."),
    OnetElement(("2.B.3.m",), ("Quality Control Analysis",), "quality_control", "Quality control", TECH,
                ("quality control", "quality assurance", "qa", "qc", "testing", "tested", "inspection", "iso 9001",
                 "standards compliance", "quality checks"),
                "Show quality work: tests, inspections or checks you carried out and the standard you worked to."),

    # ---------------- O*NET Skills: systems ----------------
    OnetElement(("2.B.4.e",), ("Judgment and Decision Making",), "judgment_decision_making", "Judgment and decision making", CORE,
                ("decision making", "decision-making", "judgement", "judgment", "prioritised", "prioritized",
                 "risk assessment", "made decisions", "approved", "cost-benefit"),
                "Add an example of a decision you made, the options and the outcome."),
    OnetElement(("2.B.4.g",), ("Systems Analysis",), "systems_analysis", "Systems analysis", TECH,
                ("systems analysis", "systems analyst", "process analysis", "workflow analysis", "business process",
                 "systems thinking", "modelled", "modeled", "simulation"),
                "Map how a real process or system works and suggest an improvement; add it as a project."),
    OnetElement(("2.B.4.h",), ("Systems Evaluation",), "systems_evaluation", "Systems evaluation", TECH,
                ("systems evaluation", "performance evaluation", "benchmarking", "metrics", "measured performance",
                 "impact assessment", "evaluated systems", "reporting"),
                "Show how you measured whether something worked, using numbers where you can."),

    # ---------------- O*NET Skills: resource management ----------------
    OnetElement(("2.B.5.a",), ("Time Management",), "time_management", "Time management", MGMT,
                ("time management", "deadlines", "met deadlines", "punctual", "scheduling", "multitasking",
                 "multi-tasking", "prioritisation", "prioritization", "planning", "part-time while studying"),
                "Show you manage time well, e.g. working while studying, or delivering projects on deadline."),
    OnetElement(("2.B.5.b",), ("Management of Financial Resources",), "financial_management", "Managing money and budgets", MGMT,
                ("budget", "budgeting", "budgets", "financial management", "cost control", "cash handling", "treasurer",
                 "expenses", "petty cash", "forecasting", "financial planning"),
                "Add any budget you managed (club, event, household business, work) and the amount."),
    OnetElement(("2.B.5.c",), ("Management of Material Resources",), "material_management", "Managing materials and stock", MGMT,
                ("inventory", "stock control", "stock management", "stocktake", "procurement", "purchasing",
                 "supply chain", "logistics", "warehouse", "asset management", "ordering"),
                "Add experience managing stock, equipment or supplies, and how you kept track of them."),
    OnetElement(("2.B.5.d",), ("Management of Personnel Resources",), "people_management", "Managing people", MGMT,
                ("supervised", "supervisor", "supervising", "managed a team", "team leader", "team lead", "led a team", "staff management", "recruitment", "recruited", "line manager"),
                "Lead a team, even a small one (club, project, church, sport), and add the team size."),

    # ---------------- O*NET Knowledge ----------------
    OnetElement(("2.C.1.a",), ("Administration and Management",), "business_management", "Business and management", KNOW,
                ("management", "business management", "business administration", "strategic planning", "operations management",
                 "project management", "leadership", "entrepreneurship", "small business", "mba", "bcom"),
                "Take a free business or project-management course and apply it to a real project or small business."),
    OnetElement(("2.C.1.b",), ("Administrative", "Clerical"), "administration", "Office administration", KNOW,
                ("administration", "administrative", "admin", "filing", "data capturing", "data capture", "data entry", "record keeping", "records management", "office management", "receptionist", "typing", "invoicing", "payroll", "records", "patient records"),
                "List office and admin experience: data capturing, filing, records or diary management."),
    OnetElement(("2.C.1.c",), ("Economics and Accounting",), "economics_accounting", "Economics and accounting", KNOW,
                ("accounting", "accountant", "bookkeeping", "bookkeeper", "economics", "financial statements", "payroll",
                 "auditing", "tax", "pastel", "sage", "quickbooks", "xero", "invoicing", "reconciliations"),
                "Show accounting knowledge: relevant subjects, bookkeeping work, or software such as Sage Pastel or Xero."),
    OnetElement(("2.C.1.d",), ("Sales and Marketing",), "sales_marketing", "Sales and marketing", KNOW,
                ("sales", "marketing", "digital marketing", "social media marketing", "advertising", "brand", "branding",
                 "promotions", "market research", "seo", "lead generation", "retail sales", "campaigns"),
                "Run a small marketing or sales effort (e.g. social media for a local business) and report the results."),
    OnetElement(("2.C.1.e",), ("Customer and Personal Service",), "customer_service", "Customer service", KNOW,
                ("customer service", "customer care", "client service", "customer experience", "complaints handling",
                 "front of house", "cashier", "waiter", "waitress", "call centre", "call center", "retail"),
                "Add customer-facing work and one example of a customer problem you solved."),
    OnetElement(("2.C.1.f",), ("Personnel and Human Resources",), "human_resources", "Human resources", KNOW,
                ("human resources", "hr", "recruitment", "recruiting", "labour relations", "labor relations",
                 "employee relations", "talent acquisition", "onboarding", "payroll", "industrial relations"),
                "Show HR knowledge through coursework or experience in recruitment, onboarding or employee records."),
    OnetElement(("2.C.2.a",), ("Production and Processing",), "production_processing", "Production and processing", KNOW,
                ("production", "manufacturing", "assembly line", "production line", "factory", "plant operator",
                 "lean manufacturing", "six sigma", "quality control"),
                "Add any production, factory or processing experience, including the products and your role."),
    OnetElement(("2.C.2.b",), ("Food Production",), "food_production", "Food production and agriculture", KNOW,
                ("agriculture", "farming", "farm", "crop production", "livestock", "horticulture", "food production",
                 "agricultural", "harvesting", "food processing"),
                "Show farming or food-production experience, even family or community gardening work."),
    OnetElement(("2.C.3.a",), ("Computers and Electronics",), "computers_electronics", "Computers and electronics", KNOW,
                ("computer literacy", "computer literate", "computers", "information technology", "electronics",
                 "hardware", "networking", "microsoft office", "ms office", "excel", "computer science"),
                "List the software and systems you can use (e.g. Microsoft Office, specific programs) under a Skills heading."),
    OnetElement(("2.C.3.b",), ("Engineering and Technology",), "engineering_technology", "Engineering and technology", KNOW,
                ("engineering", "engineer", "technical drawing", "mechanical engineering", "electrical engineering",
                 "civil engineering", "technology", "technician", "n6", "n4", "diploma in engineering"),
                "Show engineering knowledge: relevant subjects (N-levels, diploma or degree) and a hands-on technical project."),
    OnetElement(("2.C.3.c",), ("Design",), "design", "Design", KNOW,
                ("design", "designed", "graphic design", "drafting", "draughting", "autocad", "cad", "blueprints",
                 "technical drawings", "layout", "illustrator", "figma", "sketchup", "revit"),
                "Build a small design portfolio (drawings, plans or graphics) and link it in your CV."),
    OnetElement(("2.C.3.d",), ("Building and Construction",), "building_construction", "Building and construction", KNOW,
                ("construction", "bricklaying", "carpentry", "plumbing", "site work", "renovation",
                 "civil works", "roofing", "tiling", "construction site", "building construction"),
                "Add construction or building work, the trade involved and any site safety training."),
    OnetElement(("2.C.3.e",), ("Mechanical",), "mechanical", "Mechanical knowledge", KNOW,
                ("mechanical", "mechanics", "machinery", "engines", "motor mechanic", "diesel mechanic", "hydraulics",
                 "pneumatics", "fitter and turner", "millwright"),
                "Show mechanical knowledge: trade subjects, workshop experience, or machines and engines you worked on."),
    OnetElement(("2.C.4.b",), ("Physics",), "physics", "Physics", KNOW,
                ("physics", "physical science", "mechanics", "thermodynamics", "electricity", "optics"),
                "List physical science or physics results and any practical work that used them."),
    OnetElement(("2.C.4.c",), ("Chemistry",), "chemistry", "Chemistry", KNOW,
                ("chemistry", "chemical", "chemicals", "laboratory analysis", "titration", "lab technician"),
                "List chemistry subjects or lab work, and any chemical-handling or safety training."),
    OnetElement(("2.C.4.d",), ("Biology",), "biology", "Biology", KNOW,
                ("biology", "life sciences", "microbiology", "biochemistry", "anatomy", "physiology", "botany",
                 "zoology", "genetics", "ecology"),
                "List life sciences or biology subjects and any practical or lab work."),
    OnetElement(("2.C.4.e",), ("Psychology",), "psychology", "Psychology", KNOW,
                ("psychology", "behavioural", "behavioral", "counselling", "counseling", "mental health",
                 "human behaviour", "human behavior", "psychometric"),
                "Show understanding of people: psychology subjects or work supporting people's wellbeing."),
    OnetElement(("2.C.4.f",), ("Sociology and Anthropology",), "sociology", "Sociology and society", KNOW,
                ("sociology", "anthropology", "social work", "community development", "social sciences",
                 "development studies", "cultural"),
                "Add social sciences subjects or community development work."),
    OnetElement(("2.C.4.g",), ("Geography",), "geography", "Geography", KNOW,
                ("geography", "gis", "mapping", "cartography", "surveying", "spatial analysis", "arcgis", "qgis",
                 "environmental science"),
                "List geography or GIS subjects, and try a free QGIS mapping project."),
    OnetElement(("2.C.5.a",), ("Medicine and Dentistry",), "medicine", "Medicine and health", KNOW,
                ("medicine", "medical", "clinical", "nursing", "nurse", "patient care", "first aid", "healthcare",
                 "health care", "pharmacy", "dentistry", "diagnosis", "emergency care"),
                "Add health-care training or experience, starting with a first aid certificate."),
    OnetElement(("2.C.5.b",), ("Therapy and Counseling",), "therapy_counseling", "Therapy and counselling", KNOW,
                ("therapy", "therapist", "counselling", "counseling", "rehabilitation", "physiotherapy",
                 "occupational therapy", "psychotherapy", "support groups", "wellness"),
                "Show counselling or therapy training, or volunteer work supporting people."),
    OnetElement(("2.C.6",), ("Education and Training",), "education_training", "Education and training", KNOW,
                ("teaching", "lesson planning", "training facilitator", "curriculum", "facilitation", "assessor",
                 "moderator", "pgce", "b.ed", "educator", "tutoring"),
                "Add teaching, tutoring or training experience, and any assessor or facilitator qualifications."),
    OnetElement(("2.C.7.a",), ("English Language",), "english_language", "English language", KNOW,
                ("english", "english language", "grammar", "proofreading", "editing", "spelling", "comprehension"),
                "Show strong English: your English result, writing samples, or editing and proofreading work."),
    OnetElement(("2.C.7.b",), ("Foreign Language",), "other_languages", "Other languages", KNOW,
                ("isizulu", "zulu", "isixhosa", "xhosa", "afrikaans", "sesotho", "setswana", "sepedi", "xitsonga",
                 "tshivenda", "siswati", "isindebele", "french", "portuguese", "spanish", "german", "mandarin",
                 "swahili", "bilingual", "multilingual", "translation", "interpreting", "languages"),
                "List every language you speak and your level (e.g. isiZulu - fluent) in a Languages section."),
    OnetElement(("2.C.7.c",), ("Fine Arts",), "fine_arts", "Arts", KNOW,
                ("fine arts", "visual art", "music", "drama", "theatre", "theater", "dance", "painting", "photography",
                 "visual arts", "performing arts", "film"),
                "Build a portfolio of your creative work and link it in your CV."),
    OnetElement(("2.C.7.d",), ("History and Archeology",), "history", "History", KNOW,
                ("history", "historical", "archaeology", "archeology", "heritage", "archives", "museum"),
                "List history subjects or heritage and archive work."),
    OnetElement(("2.C.7.e",), ("Philosophy and Theology",), "philosophy_theology", "Philosophy and theology", KNOW,
                ("philosophy", "theology", "ethics", "religious studies", "ministry", "pastoral"),
                "List philosophy, ethics or theology studies and related work."),
    OnetElement(("2.C.8.a",), ("Public Safety and Security",), "public_safety", "Safety and security", KNOW,
                ("health and safety", "occupational health", "ohs", "security guard", "security officer", "safety officer", "psira",
                 "risk management", "fire safety", "first aid", "emergency response", "sheq"),
                "Do a health-and-safety or first aid course and add it to your CV."),
    OnetElement(("2.C.8.b",), ("Law and Government",), "law_government", "Law and government", KNOW,
                ("law", "legal", "llb", "compliance", "regulations", "regulatory", "legislation", "policy",
                 "government", "public administration", "contracts", "paralegal", "popia"),
                "Show legal or regulatory knowledge: relevant subjects, or compliance work you were part of."),
    OnetElement(("2.C.9.a",), ("Telecommunications",), "telecommunications", "Telecommunications", KNOW,
                ("telecommunications", "telecoms", "telecom", "networks", "fibre", "fiber", "radio", "wireless",
                 "cellular", "voip"),
                "Add telecoms or networking experience or certifications."),
    OnetElement(("2.C.9.b",), ("Communications and Media",), "communications_media", "Communications and media", KNOW,
                ("communications", "journalism", "public relations", "broadcasting", "social media",
                 "content creation", "editing", "newsletter", "copywriting"),
                "Create content (articles, videos, social posts) for a cause or business and link to it."),
    OnetElement(("2.C.10",), ("Transportation",), "transportation", "Transport and logistics", KNOW,
                ("transport", "transportation", "logistics", "driver's licence", "drivers licence", "driver's license",
                 "code 10", "code 14", "code 8", "pdp", "fleet", "shipping", "freight", "delivery"),
                "Add any driver's licence or PDP, and logistics or delivery experience."),
]

ELEMENT_BY_ID: Dict[str, OnetElement] = {}
ELEMENT_BY_NAME: Dict[str, OnetElement] = {}
for _el in ONET_ELEMENTS:
    for _id in _el.element_ids:
        ELEMENT_BY_ID[_id] = _el
    for _n in _el.onet_names:
        ELEMENT_BY_NAME[_n.lower()] = _el

ACTION_BY_SLUG: Dict[str, str] = {el.slug: el.action for el in ONET_ELEMENTS}


def element_for(element_id: str, element_name: str):
    """Exact lookup: by Element ID first, then by exact Element Name."""
    el = ELEMENT_BY_ID.get((element_id or "").strip())
    if el:
        return el
    return ELEMENT_BY_NAME.get((element_name or "").strip().lower())
