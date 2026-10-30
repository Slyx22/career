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
  action       - what to add or reword ON THE CV to show this skill. Never
                 "build", "take a course" or "show samples": only CV changes.

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
                "List reading comprehension under Skills. If you reviewed reports, policies or documents in a job or studies, mention it in that entry."),
    OnetElement(("2.A.1.b",), ("Active Listening",), "active_listening", "Active listening", PEOPLE,
                ("active listening", "listening skills", "customer service", "client liaison", "client relations", "customer queries", "handled queries", "needs assessment", "interviewing", "counselling", "counseling", "communication skills", "listened"),
                "List active listening under Skills."),
    OnetElement(("2.A.1.c",), ("Writing",), "writing", "Writing", CORE,
                ("writing", "written communication", "report writing", "wrote", "drafted", "documentation", "copywriting", "technical writing", "minutes", "proposals", "content writing", "blog", "reported", "reports", "prepared reports"),
                "List written communication under Skills. If you wrote reports, minutes or other documents in a job, mention it in that job's entry."),
    OnetElement(("2.A.1.d",), ("Speaking",), "speaking", "Speaking", PEOPLE,
                ("public speaking", "presentation skills", "presentations", "presented", "verbal communication",
                 "oral communication", "communication skills", "facilitated", "spokesperson", "debating", "debate"),
                "List verbal communication or public speaking under Skills. If you presented to groups, mention it in that entry."),
    OnetElement(("2.A.1.e", "2.C.4.a"), ("Mathematics",), "mathematics", "Mathematics", CORE,
                ("mathematics", "maths", "math", "calculus", "algebra", "statistics", "statistical", "quantitative", "numerical", "numeracy", "calculations", "financial modelling", "financial modeling", "mathematical", "reconciliations", "financial statements", "data analysis", "budgeting"),
                "Add your Mathematics or Maths Literacy result under Education. If you worked with numbers in a job (cash, stock, budgets), mention it in that job's entry."),
    OnetElement(("2.A.1.f",), ("Science",), "science", "Scientific method", CORE,
                ("scientific", "science", "laboratory", "lab work", "experiments", "experimental", "research methodology",
                 "hypothesis", "data collection", "fieldwork"),
                "Add your science subjects and results under Education. If you did lab or field work, mention it in that entry."),

    # ---------------- O*NET Skills: process ----------------
    OnetElement(("2.A.2.a",), ("Critical Thinking",), "critical_thinking", "Critical thinking", CORE,
                ("critical thinking", "problem solving", "problem-solving", "analytical", "analytical thinking",
                 "analysis", "analysed", "analyzed", "evaluated", "root cause", "assessed"),
                "List critical thinking or problem solving under Skills."),
    OnetElement(("2.A.2.b",), ("Active Learning",), "active_learning", "Active learning", CORE,
                ("self-taught", "self taught", "quick learner", "fast learner", "upskilled", "certification", "certified",
                 "online course", "coursera", "udemy", "edx", "short course", "continuous learning", "workshop"),
                "List any courses or certificates you've completed under a Certifications heading, with the year."),
    OnetElement(("2.A.2.c",), ("Learning Strategies",), "learning_strategies", "Learning strategies", PEOPLE,
                ("tutoring", "tutor", "mentoring", "mentored", "coaching", "coached", "training others", "trained staff",
                 "lesson planning", "study groups", "curriculum"),
                "If you've tutored, mentored or trained anyone, add it under Experience or Volunteering, and list mentoring under Skills."),
    OnetElement(("2.A.2.d",), ("Monitoring",), "monitoring", "Monitoring performance", CORE,
                ("monitored", "monitoring", "tracked", "tracking", "kpi", "kpis", "performance review", "audit", "audited", "evaluation", "progress reports", "compliance checks", "variances", "vital signs", "reconciliations"),
                "If you tracked targets, quality or progress in a job, add that to the job's entry with the measure you used."),

    # ---------------- O*NET Skills: social ----------------
    OnetElement(("2.B.1.a",), ("Social Perceptiveness",), "social_perceptiveness", "Social perceptiveness", PEOPLE,
                ("empathy", "empathetic", "interpersonal skills", "interpersonal", "emotional intelligence",
                 "patient care", "community work", "volunteer", "volunteered", "volunteering", "people skills"),
                "List interpersonal skills under Skills."),
    OnetElement(("2.B.1.b",), ("Coordination",), "coordination", "Coordination", PEOPLE,
                ("coordinated", "coordination", "coordinator", "teamwork", "team player", "collaborated", "collaboration",
                 "cross-functional", "liaised", "scheduling", "organised events", "organized events", "event planning"),
                "List coordination or organisation under Skills. If you organised people, shifts or events, mention it in that entry."),
    OnetElement(("2.B.1.c",), ("Persuasion",), "persuasion", "Persuasion", PEOPLE,
                ("persuasion", "persuasive", "influenced", "convinced", "pitching", "pitched", "advocacy", "campaign",
                 "sales", "fundraising", "lobbying"),
                "List persuasion or sales skills under Skills. If you sold, pitched or fundraised, add the result to that entry."),
    OnetElement(("2.B.1.d",), ("Negotiation",), "negotiation", "Negotiation", PEOPLE,
                ("negotiation", "negotiated", "negotiating", "conflict resolution", "mediation", "mediated",
                 "contract negotiation", "procurement", "dispute resolution"),
                "List negotiation or conflict resolution under Skills."),
    OnetElement(("2.B.1.e",), ("Instructing",), "instructing", "Instructing others", PEOPLE,
                ("instructing", "instructed", "teaching", "taught", "trained staff", "trained new", "trained others", "trained employees", "onboarding",
                 "facilitator", "teacher", "lecturer", "tutor"),
                "If you've trained or taught others, add it to that job's entry with how many people, and list training under Skills."),
    OnetElement(("2.B.1.f",), ("Service Orientation",), "service_orientation", "Service orientation", PEOPLE,
                ("customer service", "client service", "customer care", "service delivery", "helpdesk", "help desk",
                 "front desk", "reception", "hospitality", "call centre", "call center", "customer satisfaction"),
                "List customer service under Skills. If you've worked with customers or the public, make sure that job is on your CV."),

    # ---------------- O*NET Skills: complex problem solving & technical ----------------
    OnetElement(("2.B.2.i",), ("Complex Problem Solving",), "complex_problem_solving", "Complex problem solving", CORE,
                ("complex problem solving", "problem solving", "problem-solving", "solved", "resolved", "troubleshot",
                 "improved process", "process improvement", "innovation"),
                "List problem solving under Skills."),
    OnetElement(("2.B.3.a",), ("Operations Analysis",), "operations_analysis", "Operations analysis", TECH,
                ("requirements gathering", "requirements analysis", "business analysis", "needs analysis",
                 "process mapping", "user requirements", "business requirements", "gap analysis"),
                "If you gathered requirements or worked out what users needed, mention it in that job or project entry."),
    OnetElement(("2.B.3.b",), ("Technology Design",), "technology_design", "Technology design", TECH,
                ("designed", "prototype", "prototyping", "product design", "system design", "solution design",
                 "engineering design", "cad", "user experience", "ux design"),
                "If you designed equipment, systems or solutions, add it to that job or project entry with what it did."),
    OnetElement(("2.B.3.c",), ("Equipment Selection",), "equipment_selection", "Equipment selection", TECH,
                ("equipment selection", "selected equipment", "specified equipment", "tools selection",
                 "procurement of equipment", "sourcing equipment", "specification"),
                "If you chose or specified tools, equipment or materials, mention it in that job's entry."),
    OnetElement(("2.B.3.d",), ("Installation",), "installation", "Installation", TECH,
                ("installation", "installed", "installing", "commissioning", "fitted", "fitting",
                 "wiring", "assembled", "assembly"),
                "If you've installed equipment, software, wiring or fittings, add what you installed to that job's entry."),
    OnetElement(("2.B.3.e",), ("Programming",), "programming", "Programming", TECH,
                ("programming", "coding", "software development", "scripting", "developer", "programmer", "github",
                 "python", "java", "javascript", "c++", "c#", "sql", "vba"),
                "List the programming languages you use under Skills, and name them in the jobs or projects where you used them."),
    OnetElement(("2.B.3.g",), ("Operations Monitoring",), "operations_monitoring", "Operations monitoring", TECH,
                ("operations monitoring", "monitored systems", "monitored equipment", "gauges", "readings", "dashboards",
                 "system monitoring", "control room", "inspections", "inspected"),
                "If you monitored equipment, systems or dashboards, mention it in that job's entry."),
    OnetElement(("2.B.3.h",), ("Operation and Control",), "operation_and_control", "Operating equipment", TECH,
                ("operated", "operating", "operator", "machine operation", "forklift", "driving", "drove",
                 "control systems", "plant operation", "heavy machinery"),
                "List the machines, vehicles or systems you can operate under Skills, with any licence or certificate you hold."),
    OnetElement(("2.B.3.j",), ("Equipment Maintenance",), "equipment_maintenance", "Equipment maintenance", TECH,
                ("maintenance", "maintained", "preventive maintenance", "servicing", "serviced", "upkeep",
                 "lubrication", "maintenance schedule"),
                "If you've maintained equipment, add what you looked after and how often to that job's entry."),
    OnetElement(("2.B.3.k",), ("Troubleshooting",), "troubleshooting", "Troubleshooting", TECH,
                ("troubleshooting", "troubleshoot", "troubleshot", "diagnosed", "diagnostics", "fault finding",
                 "fault-finding", "debugging", "debugged", "technical support", "it support"),
                "List troubleshooting under Skills. If you diagnosed and fixed faults, mention what kind in that job's entry."),
    OnetElement(("2.B.3.l",), ("Repairing",), "repairing", "Repairing", TECH,
                ("repair", "repaired", "repairing", "repairs", "replaced parts", "refurbished", "overhauled",
                 "mechanic", "artisan"),
                "If you've done repair work, add what you repaired to that job's entry, and list any trade training under Education."),
    OnetElement(("2.B.3.m",), ("Quality Control Analysis",), "quality_control", "Quality control", TECH,
                ("quality control", "quality assurance", "qa", "qc", "testing", "tested", "inspection", "iso 9001",
                 "standards compliance", "quality checks"),
                "If you did inspections, tests or quality checks, add them to that job's entry with the standard you worked to."),

    # ---------------- O*NET Skills: systems ----------------
    OnetElement(("2.B.4.e",), ("Judgment and Decision Making",), "judgment_decision_making", "Judgment and decision making", CORE,
                ("decision making", "decision-making", "judgement", "judgment", "prioritised", "prioritized",
                 "risk assessment", "made decisions", "approved", "cost-benefit"),
                "List decision making under Skills."),
    OnetElement(("2.B.4.g",), ("Systems Analysis",), "systems_analysis", "Systems analysis", TECH,
                ("systems analysis", "systems analyst", "process analysis", "workflow analysis", "business process",
                 "systems thinking", "modelled", "modeled", "simulation"),
                "If you analysed or improved a process or system, add it to that job or project entry with the improvement."),
    OnetElement(("2.B.4.h",), ("Systems Evaluation",), "systems_evaluation", "Systems evaluation", TECH,
                ("systems evaluation", "performance evaluation", "benchmarking", "metrics", "measured performance",
                 "impact assessment", "evaluated systems", "reporting"),
                "If you measured whether something worked, add the result to that job or project entry, with a number where you can."),

    # ---------------- O*NET Skills: resource management ----------------
    OnetElement(("2.B.5.a",), ("Time Management",), "time_management", "Time management", MGMT,
                ("time management", "deadlines", "met deadlines", "punctual", "scheduling", "multitasking",
                 "multi-tasking", "prioritisation", "prioritization", "planning", "part-time while studying"),
                "List time management under Skills. If you worked while studying, make sure both are on your CV with dates."),
    OnetElement(("2.B.5.b",), ("Management of Financial Resources",), "financial_management", "Managing money and budgets", MGMT,
                ("budget", "budgeting", "budgets", "financial management", "cost control", "cash handling", "treasurer",
                 "expenses", "petty cash", "forecasting", "financial planning"),
                "If you've managed a budget, cash or money in any role, add it to that entry with the amount."),
    OnetElement(("2.B.5.c",), ("Management of Material Resources",), "material_management", "Managing materials and stock", MGMT,
                ("inventory", "stock control", "stock management", "stocktake", "procurement", "purchasing",
                 "supply chain", "logistics", "warehouse", "asset management", "ordering"),
                "If you've managed stock, supplies or equipment, add it to that job's entry."),
    OnetElement(("2.B.5.d",), ("Management of Personnel Resources",), "people_management", "Managing people", MGMT,
                ("supervised", "supervisor", "supervising", "managed a team", "team leader", "team lead", "led a team", "staff management", "recruitment", "recruited", "line manager"),
                "If you've led or supervised people, add it to that entry with the team size, and list leadership under Skills."),

    # ---------------- O*NET Knowledge ----------------
    OnetElement(("2.C.1.a",), ("Administration and Management",), "business_management", "Business and management", KNOW,
                ("management", "business management", "business administration", "strategic planning", "operations management",
                 "project management", "leadership", "entrepreneurship", "small business", "mba", "bcom"),
                "Add any business or management subjects under Education. If you've run or helped run a business, add it under Experience."),
    OnetElement(("2.C.1.b",), ("Administrative", "Clerical"), "administration", "Office administration", KNOW,
                ("administration", "administrative", "admin", "filing", "data capturing", "data capture", "data entry", "record keeping", "records management", "office management", "receptionist", "typing", "invoicing", "payroll", "records", "patient records"),
                "If you've done admin work (filing, data capturing, records, diaries), add it to that job's entry, and list admin skills under Skills."),
    OnetElement(("2.C.1.c",), ("Economics and Accounting",), "economics_accounting", "Economics and accounting", KNOW,
                ("accounting", "accountant", "bookkeeping", "bookkeeper", "economics", "financial statements", "payroll",
                 "auditing", "tax", "pastel", "sage", "quickbooks", "xero", "invoicing", "reconciliations"),
                "Add your Accounting or Economics subjects and results under Education, and list accounting software you use (e.g. Sage Pastel, Xero) under Skills."),
    OnetElement(("2.C.1.d",), ("Sales and Marketing",), "sales_marketing", "Sales and marketing", KNOW,
                ("sales", "marketing", "digital marketing", "social media marketing", "advertising", "brand", "branding",
                 "promotions", "market research", "seo", "lead generation", "retail sales", "campaigns"),
                "If you've worked in sales or marketing, add it to that job's entry with a result, and list sales or marketing under Skills."),
    OnetElement(("2.C.1.e",), ("Customer and Personal Service",), "customer_service", "Customer service", KNOW,
                ("customer service", "customer care", "client service", "customer experience", "complaints handling", "patient care",
                 "front of house", "cashier", "waiter", "waitress", "call centre", "call center", "retail"),
                "List customer service under Skills. If you've worked with customers or the public, make sure that job is on your CV."),
    OnetElement(("2.C.1.f",), ("Personnel and Human Resources",), "human_resources", "Human resources", KNOW,
                ("human resources", "hr", "recruitment", "recruiting", "labour relations", "labor relations",
                 "employee relations", "talent acquisition", "onboarding", "payroll", "industrial relations"),
                "Add any HR subjects under Education. If you've worked in recruitment, onboarding or staff records, add it to that job's entry."),
    OnetElement(("2.C.2.a",), ("Production and Processing",), "production_processing", "Production and processing", KNOW,
                ("production", "manufacturing", "assembly line", "production line", "factory", "plant operator",
                 "lean manufacturing", "six sigma", "quality control"),
                "If you've worked in production, a factory or processing, add it under Experience with the products and your role."),
    OnetElement(("2.C.2.b",), ("Food Production",), "food_production", "Food production and agriculture", KNOW,
                ("agriculture", "farming", "farm", "crop production", "livestock", "horticulture", "food production",
                 "agricultural", "harvesting", "food processing"),
                "If you've worked in farming or food production (including family or community work), add it under Experience."),
    OnetElement(("2.C.3.a",), ("Computers and Electronics",), "computers_electronics", "Computers and electronics", KNOW,
                ("computer literacy", "computer literate", "computers", "information technology", "electronics",
                 "hardware", "networking", "microsoft office", "ms office", "excel", "computer science"),
                "List the software and computer systems you can use under Skills."),
    OnetElement(("2.C.3.b",), ("Engineering and Technology",), "engineering_technology", "Engineering and technology", KNOW,
                ("engineering", "engineer", "technical drawing", "mechanical engineering", "electrical engineering",
                 "civil engineering", "technology", "technician", "n6", "n4", "diploma in engineering"),
                "Add your engineering or technical subjects (N-levels, diploma or degree) under Education."),
    OnetElement(("2.C.3.c",), ("Design",), "design", "Design", KNOW,
                ("design", "designed", "graphic design", "drafting", "draughting", "autocad", "cad", "blueprints",
                 "technical drawings", "layout", "illustrator", "figma", "sketchup", "revit"),
                "List the design software or methods you use under Skills, and add design subjects under Education."),
    OnetElement(("2.C.3.d",), ("Building and Construction",), "building_construction", "Building and construction", KNOW,
                ("construction", "bricklaying", "carpentry", "plumbing", "site work", "renovation",
                 "civil works", "roofing", "tiling", "construction site", "building construction"),
                "If you've done construction or building work, add it under Experience with the trade, and list site safety training under Certifications."),
    OnetElement(("2.C.3.e",), ("Mechanical",), "mechanical", "Mechanical knowledge", KNOW,
                ("mechanical", "mechanics", "machinery", "engines", "motor mechanic", "diesel mechanic", "hydraulics",
                 "pneumatics", "fitter and turner", "millwright"),
                "Add trade or technical subjects under Education. If you've worked on machines or engines, add it to that job's entry."),
    OnetElement(("2.C.4.b",), ("Physics",), "physics", "Physics", KNOW,
                ("physics", "physical science", "mechanics", "thermodynamics", "electricity", "optics"),
                "Add your Physical Sciences or physics results under Education."),
    OnetElement(("2.C.4.c",), ("Chemistry",), "chemistry", "Chemistry", KNOW,
                ("chemistry", "chemical", "chemicals", "laboratory analysis", "titration", "lab technician"),
                "Add your chemistry subjects under Education, and any chemical-handling or safety training under Certifications."),
    OnetElement(("2.C.4.d",), ("Biology",), "biology", "Biology", KNOW,
                ("biology", "life sciences", "microbiology", "biochemistry", "anatomy", "physiology", "botany",
                 "zoology", "genetics", "ecology"),
                "Add your Life Sciences or biology subjects and results under Education."),
    OnetElement(("2.C.4.e",), ("Psychology",), "psychology", "Psychology", KNOW,
                ("psychology", "behavioural", "behavioral", "counselling", "counseling", "mental health",
                 "human behaviour", "human behavior", "psychometric"),
                "Add any psychology subjects under Education. If you've supported people's wellbeing, add it under Experience or Volunteering."),
    OnetElement(("2.C.4.f",), ("Sociology and Anthropology",), "sociology", "Sociology and society", KNOW,
                ("sociology", "anthropology", "social work", "community development", "social sciences",
                 "development studies", "cultural"),
                "Add social science subjects under Education. If you've done community work, add it under Experience or Volunteering."),
    OnetElement(("2.C.4.g",), ("Geography",), "geography", "Geography", KNOW,
                ("geography", "gis", "mapping", "cartography", "surveying", "spatial analysis", "arcgis", "qgis",
                 "environmental science"),
                "Add your Geography or GIS subjects and results under Education, and any GIS software under Skills."),
    OnetElement(("2.C.5.a",), ("Medicine and Dentistry",), "medicine", "Medicine and health", KNOW,
                ("medicine", "medical", "clinical", "nursing", "nurse", "patient care", "first aid", "healthcare",
                 "health care", "pharmacy", "dentistry", "diagnosis", "emergency care"),
                "Add any health-care training under Education or Certifications (including first aid), and health-care work under Experience."),
    OnetElement(("2.C.5.b",), ("Therapy and Counseling",), "therapy_counseling", "Therapy and counselling", KNOW,
                ("therapy", "therapist", "counselling", "counseling", "rehabilitation", "physiotherapy",
                 "occupational therapy", "psychotherapy", "support groups", "wellness"),
                "Add any counselling training under Education or Certifications. If you've supported people, add it under Experience or Volunteering."),
    OnetElement(("2.C.6",), ("Education and Training",), "education_training", "Education and training", KNOW,
                ("teaching", "lesson planning", "training facilitator", "curriculum", "facilitation", "assessor",
                 "moderator", "pgce", "b.ed", "educator", "tutoring"),
                "If you've taught, tutored or trained people, add it under Experience, and any assessor or facilitator qualification under Certifications."),
    OnetElement(("2.C.7.a",), ("English Language",), "english_language", "English language", KNOW,
                ("english", "english language", "grammar", "proofreading", "editing", "spelling", "comprehension"),
                "Add your English result under Education, and list English with your level under Languages."),
    OnetElement(("2.C.7.b",), ("Foreign Language",), "other_languages", "Other languages", KNOW,
                ("isizulu", "zulu", "isixhosa", "xhosa", "afrikaans", "sesotho", "setswana", "sepedi", "xitsonga",
                 "tshivenda", "siswati", "isindebele", "french", "portuguese", "spanish", "german", "mandarin",
                 "swahili", "bilingual", "multilingual", "translation", "interpreting", "languages"),
                "List every language you speak and your level (e.g. isiZulu, fluent) under Languages."),
    OnetElement(("2.C.7.c",), ("Fine Arts",), "fine_arts", "Arts", KNOW,
                ("fine arts", "visual art", "music", "drama", "theatre", "theater", "dance", "painting", "photography",
                 "visual arts", "performing arts", "film"),
                "Add any arts subjects under Education, and list the creative skills and tools you use under Skills."),
    OnetElement(("2.C.7.d",), ("History and Archeology",), "history", "History", KNOW,
                ("history", "historical", "archaeology", "archeology", "heritage", "archives", "museum"),
                "Add history subjects under Education. If you've done heritage or archive work, add it under Experience."),
    OnetElement(("2.C.7.e",), ("Philosophy and Theology",), "philosophy_theology", "Philosophy and theology", KNOW,
                ("philosophy", "theology", "ethics", "religious studies", "ministry", "pastoral"),
                "Add any philosophy, ethics or theology studies under Education."),
    OnetElement(("2.C.8.a",), ("Public Safety and Security",), "public_safety", "Safety and security", KNOW,
                ("health and safety", "occupational health", "ohs", "security guard", "security officer", "safety officer", "psira",
                 "risk management", "fire safety", "first aid", "emergency response", "sheq"),
                "List any safety, security or first aid certificates under Certifications, with the year."),
    OnetElement(("2.C.8.b",), ("Law and Government",), "law_government", "Law and government", KNOW,
                ("law", "legal", "llb", "compliance", "regulations", "regulatory", "legislation", "policy",
                 "government", "public administration", "contracts", "paralegal", "popia"),
                "Add any law subjects under Education. If you've done compliance or legal admin work, add it to that job's entry."),
    OnetElement(("2.C.9.a",), ("Telecommunications",), "telecommunications", "Telecommunications", KNOW,
                ("telecommunications", "telecoms", "telecom", "networks", "fibre", "fiber", "radio", "wireless",
                 "cellular", "voip"),
                "If you've worked with telecoms or networks, add it under Experience, and any certifications under Certifications."),
    OnetElement(("2.C.9.b",), ("Communications and Media",), "communications_media", "Communications and media", KNOW,
                ("communications", "journalism", "public relations", "broadcasting", "social media",
                 "content creation", "editing", "newsletter", "copywriting"),
                "If you've created content or run social media for anyone, add it under Experience, and list the platforms and tools under Skills."),
    OnetElement(("2.C.10",), ("Transportation",), "transportation", "Transport and logistics", KNOW,
                ("transport", "transportation", "logistics", "driver's licence", "drivers licence", "driver's license",
                 "code 10", "code 14", "code 8", "pdp", "fleet", "shipping", "freight", "delivery"),
                "Add your driver's licence code (and PrDP if you have one) and any logistics or delivery work under Experience."),
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
