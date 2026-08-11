"""
app/ml/data.py — Role keywords and interview questions.

This is the "brain" of JobCatch — pure Python dictionaries.
No ML library needed. Just keyword matching.

ROLE_KEYWORDS: Used for prediction + skill extraction + gap analysis.
INTERVIEW_QUESTIONS: Used on the Interview Prep page.
SUGGESTED_SKILLS: Additional skills to learn beyond what's on the resume.
"""

# ----------------------------------------------------------------
# Role → Keywords dictionary
# Each role has ~15 keywords. We count how many appear in the resume.
# The role with the highest count wins.
# ----------------------------------------------------------------
ROLE_KEYWORDS = {
    "Python Developer": [
        "python", "django", "flask", "fastapi", "pandas", "numpy",
        "rest api", "sqlalchemy", "celery", "pytest", "pip", "virtualenv",
        "asyncio", "pydantic", "uvicorn"
    ],
    "Data Science": [
        "machine learning", "data analysis", "python", "tensorflow", "keras",
        "scikit-learn", "pandas", "numpy", "matplotlib", "seaborn", "jupyter",
        "statistics", "regression", "classification", "clustering", "nlp",
        "deep learning", "neural network"
    ],
    "Web Designing": [
        "html", "css", "javascript", "figma", "adobe xd", "photoshop",
        "ui", "ux", "responsive", "bootstrap", "tailwind", "wireframe",
        "prototyping", "typography", "color theory"
    ],
    "Java Developer": [
        "java", "spring", "spring boot", "hibernate", "maven", "gradle",
        "jpa", "rest", "microservices", "junit", "mysql", "tomcat",
        "multithreading", "jdbc", "jvm"
    ],
    "DevOps Engineer": [
        "docker", "kubernetes", "ci/cd", "jenkins", "ansible", "terraform",
        "aws", "azure", "linux", "bash", "git", "helm", "prometheus",
        "grafana", "nginx"
    ],
    "HR": [
        "recruitment", "onboarding", "payroll", "employee relations",
        "performance management", "hr policies", "talent acquisition",
        "labor law", "training", "compensation", "succession planning",
        "hris", "attrition", "workforce", "compliance"
    ],
    "Testing": [
        "manual testing", "test cases", "bug report", "selenium", "jira",
        "regression testing", "functional testing", "qa", "test plan",
        "postman", "api testing", "performance testing", "agile", "scrum",
        "cucumber"
    ],
    "Automation Testing": [
        "selenium", "cypress", "pytest", "robot framework", "appium",
        "testng", "junit", "ci/cd", "api automation", "rest assured",
        "jenkins", "jira", "agile", "bdd", "gherkin"
    ],
    "Database": [
        "sql", "mysql", "postgresql", "mongodb", "oracle", "pl/sql",
        "stored procedures", "indexing", "normalization", "etl",
        "database design", "query optimization", "nosql", "redis", "cassandra"
    ],
    "Network Security Engineer": [
        "firewall", "vpn", "intrusion detection", "penetration testing",
        "cybersecurity", "tcp/ip", "network monitoring", "siem", "nmap",
        "wireshark", "ssl/tls", "zero trust", "vulnerability assessment",
        "cisco", "fortinet"
    ],
    "Mechanical Engineer": [
        "autocad", "solidworks", "catia", "ansys", "thermodynamics",
        "fluid mechanics", "manufacturing", "cnc", "finite element analysis",
        "product design", "quality control", "six sigma", "lean", "cad", "cam"
    ],
    "Civil Engineer": [
        "autocad", "structural analysis", "concrete", "staad pro", "revit",
        "construction management", "surveying", "geotechnical", "highway",
        "project management", "quantity estimation", "bim", "primavera",
        "rebar", "foundation"
    ],
    "Electrical Engineering": [
        "circuit design", "matlab", "plc", "scada", "power systems",
        "embedded systems", "microcontroller", "arduino", "pcb design",
        "motor drives", "hmi", "transformer", "relay", "vfd", "hvac"
    ],
    "Blockchain": [
        "solidity", "ethereum", "smart contracts", "web3", "defi",
        "nft", "hyperledger", "consensus", "cryptography", "truffle",
        "hardhat", "metamask", "ipfs", "dao", "tokenization"
    ],
    "DotNet Developer": [
        "c#", ".net", "asp.net", "entity framework", "linq", "mvc",
        "wpf", "wcf", "sql server", "azure", "rest api", "microservices",
        "visual studio", "blazor", "signalr"
    ],
    "Hadoop": [
        "hadoop", "mapreduce", "hive", "pig", "hdfs", "spark",
        "yarn", "zookeeper", "sqoop", "flume", "kafka", "hbase",
        "oozie", "big data", "cloudera"
    ],
    "ETL Developer": [
        "etl", "informatica", "talend", "ssis", "datastage", "sql",
        "data warehouse", "pentaho", "data pipeline", "oracle",
        "transformation", "data cleansing", "staging", "olap", "oltp"
    ],
    "Operations Manager": [
        "operations management", "supply chain", "logistics", "process improvement",
        "kpi", "lean", "six sigma", "erp", "sap", "inventory management",
        "vendor management", "project management", "budgeting", "team leadership",
        "cost reduction"
    ],
    "Business Analyst": [
        "requirements gathering", "use case", "user stories", "agile",
        "scrum", "sql", "power bi", "tableau", "gap analysis", "brd",
        "stakeholder management", "wireframes", "jira", "process mapping",
        "data analysis"
    ],
    "SAP Developer": [
        "sap", "abap", "sap hana", "sap fiori", "bapi", "idoc",
        "smartforms", "sap bw", "sap mm", "sap sd", "sap fi",
        "sap basis", "odata", "rfc", "enhancement"
    ],
    "Sales": [
        "sales", "crm", "lead generation", "cold calling", "negotiation",
        "customer acquisition", "salesforce", "revenue", "pipeline",
        "account management", "b2b", "b2c", "quotas", "upselling",
        "client relationship"
    ],
    "Advocate": [
        "litigation", "legal research", "contract drafting", "court proceedings",
        "criminal law", "civil law", "corporate law", "intellectual property",
        "due diligence", "legal advice", "arbitration", "compliance",
        "legal documentation", "bar council", "ipc"
    ],
    "Arts": [
        "painting", "drawing", "sculpture", "photography", "graphic design",
        "illustration", "adobe illustrator", "adobe photoshop", "animation",
        "creativity", "portfolio", "exhibition", "fine arts", "sketch", "art direction"
    ],
    "Health and fitness": [
        "nutrition", "personal training", "yoga", "fitness assessment",
        "exercise physiology", "weight management", "rehabilitation",
        "sports coaching", "wellness", "anatomy", "physiology", "gym",
        "cardio", "strength training", "diet planning"
    ],
    "PMO": [
        "project management", "pmp", "prince2", "agile", "waterfall",
        "risk management", "stakeholder management", "project planning",
        "ms project", "jira", "resource allocation", "budget management",
        "governance", "reporting", "change management"
    ],
}

# ----------------------------------------------------------------
# Interview questions per role
# ----------------------------------------------------------------
INTERVIEW_QUESTIONS = {
    "Python Developer": [
        {"q": "What is the difference between a list and a tuple in Python?",
         "a": "Lists are mutable (changeable) and use square brackets []. Tuples are immutable (cannot be changed) and use parentheses (). Tuples are faster and used for fixed data."},
        {"q": "What is a decorator in Python?",
         "a": "A decorator is a function that wraps another function to add extra behaviour without modifying it. It uses the @decorator syntax above a function definition."},
        {"q": "Explain the difference between `is` and `==`.",
         "a": "`==` checks if two values are equal. `is` checks if two variables point to the exact same object in memory."},
        {"q": "What is a virtual environment and why do we use it?",
         "a": "A virtual environment is an isolated Python installation for a specific project. It lets each project have its own dependencies without conflicts."},
        {"q": "What is the difference between Django and Flask?",
         "a": "Django is a full-featured framework with ORM, admin panel, and auth built-in (batteries included). Flask is a micro-framework — lightweight, with only the essentials, and you add what you need."},
    ],
    "Data Science": [
        {"q": "What is the difference between supervised and unsupervised learning?",
         "a": "Supervised learning trains on labelled data (input + correct output). Unsupervised learning finds patterns in data that has no labels."},
        {"q": "What is overfitting and how do you prevent it?",
         "a": "Overfitting is when a model learns the training data too well and performs poorly on new data. We prevent it with techniques like cross-validation, regularization, and using more training data."},
        {"q": "What is TF-IDF?",
         "a": "TF-IDF (Term Frequency-Inverse Document Frequency) is a technique to convert text into numbers. Words that appear often in one document but rarely in others get a high score, making them more meaningful."},
        {"q": "Explain the bias-variance tradeoff.",
         "a": "High bias = model is too simple (underfits). High variance = model is too complex (overfits). The goal is to find the sweet spot with low bias and low variance."},
        {"q": "What is a confusion matrix?",
         "a": "A table that shows how many predictions were correct (True Positives/Negatives) and incorrect (False Positives/Negatives). It helps evaluate a classification model's performance."},
    ],
    "Web Designing": [
        {"q": "What is the CSS Box Model?",
         "a": "Every HTML element is a box with four layers: Content → Padding → Border → Margin. Understanding this is key to controlling spacing and layout."},
        {"q": "What is responsive web design?",
         "a": "Designing websites that look good on all screen sizes using techniques like media queries, flexible grids, and fluid images."},
        {"q": "What is the difference between Flexbox and CSS Grid?",
         "a": "Flexbox is one-dimensional (row OR column). CSS Grid is two-dimensional (rows AND columns). Use Flexbox for components; use Grid for full page layouts."},
        {"q": "What is a wireframe?",
         "a": "A wireframe is a simple black-and-white sketch of a web page's layout — no colors or graphics. It focuses on structure and user flow before visual design begins."},
        {"q": "What is UI vs UX?",
         "a": "UI (User Interface) is how it looks — colors, fonts, buttons. UX (User Experience) is how it works — the journey a user takes to complete a task."},
    ],
    "Java Developer": [
        {"q": "What is the difference between JDK, JRE, and JVM?",
         "a": "JVM (Java Virtual Machine) runs bytecode. JRE (Java Runtime Environment) = JVM + libraries. JDK (Java Development Kit) = JRE + compiler + tools to write Java."},
        {"q": "What is the difference between an interface and an abstract class?",
         "a": "An interface defines a contract (what to do, not how). An abstract class can have some implemented methods. A class can implement multiple interfaces but extend only one abstract class."},
        {"q": "What is Spring Boot?",
         "a": "Spring Boot is a framework that makes it easy to build production-ready Spring applications. It handles configuration automatically so you can focus on business logic."},
        {"q": "What is a NullPointerException and how do you avoid it?",
         "a": "A NullPointerException happens when you try to use a variable that is null. Avoid it by using null checks, Optional, or initializing variables properly."},
        {"q": "Explain the concept of multithreading in Java.",
         "a": "Multithreading allows a program to run multiple threads simultaneously, improving performance. Threads share the same memory, so we use synchronization to avoid conflicts."},
    ],
    "DevOps Engineer": [
        {"q": "What is the difference between containerization and virtualization?",
         "a": "Virtualization creates a full virtual machine with its own OS. Containerization (Docker) shares the host OS kernel — containers are lighter and start faster."},
        {"q": "What is CI/CD?",
         "a": "CI (Continuous Integration) = automatically build and test code after every commit. CD (Continuous Delivery/Deployment) = automatically deploy the tested code to production or staging."},
        {"q": "What is Kubernetes and why is it used?",
         "a": "Kubernetes (K8s) is a system for managing Docker containers at scale — it handles deployment, scaling, and self-healing (restarting failed containers)."},
        {"q": "What is Infrastructure as Code (IaC)?",
         "a": "Managing and provisioning infrastructure (servers, networks) using code files instead of manual processes. Terraform and Ansible are common IaC tools."},
        {"q": "What is the purpose of a load balancer?",
         "a": "A load balancer distributes incoming traffic across multiple servers so no single server is overwhelmed, improving performance and fault tolerance."},
    ],
    "Testing": [
        {"q": "What is the difference between functional and non-functional testing?",
         "a": "Functional testing checks what the system does (does the login work?). Non-functional testing checks how it performs (how fast? how secure?)."},
        {"q": "What is regression testing?",
         "a": "Re-running previously passed test cases after a code change to ensure the new change didn't break anything that worked before."},
        {"q": "What is a test plan?",
         "a": "A document that outlines the scope, objectives, approach, resources, and schedule for testing. It's the roadmap for the entire testing process."},
        {"q": "What is the difference between black-box and white-box testing?",
         "a": "Black-box: tester doesn't know the internal code — tests from user's perspective. White-box: tester knows the code and tests internal logic/paths."},
        {"q": "What is a bug life cycle?",
         "a": "The stages a bug goes through: New → Assigned → Open → Fixed → Retest → Closed (or Reopened if the fix didn't work)."},
    ],
    "HR": [
        {"q": "What is the full cycle of recruitment?",
         "a": "Job analysis → Job posting → Sourcing candidates → Screening → Interviews → Selection → Offer → Onboarding."},
        {"q": "How do you handle a conflict between two employees?",
         "a": "Listen to both sides privately, identify the root cause, mediate a discussion, agree on a resolution, document it, and follow up."},
        {"q": "What is attrition and how do you reduce it?",
         "a": "Attrition is the rate at which employees leave the company. Reduce it through competitive salaries, career growth, recognition, good work culture, and regular feedback."},
        {"q": "What is an HRIS?",
         "a": "Human Resource Information System — software used to manage employee data, payroll, attendance, benefits, and recruitment in one place."},
        {"q": "What is the difference between training and development?",
         "a": "Training is short-term, job-specific skill building (e.g., how to use a tool). Development is long-term growth for future roles (e.g., leadership skills)."},
    ],
    "Business Analyst": [
        {"q": "What is a BRD?",
         "a": "Business Requirements Document — a formal document that describes what a business needs from a system or process. It is the foundation for development."},
        {"q": "What is the difference between a use case and a user story?",
         "a": "A use case describes all interactions between a user and a system in detail. A user story is a short, simple description from the user's perspective: 'As a user, I want to... so that...'"},
        {"q": "What is gap analysis?",
         "a": "Comparing the current state (what we have) vs the desired state (what we need) to identify the gaps that need to be addressed."},
        {"q": "What tools do Business Analysts commonly use?",
         "a": "Jira, Confluence (documentation), Visio/Lucidchart (process mapping), SQL (data queries), Excel/Google Sheets, and Power BI/Tableau for data visualization."},
        {"q": "How do you handle changing requirements?",
         "a": "Document the change request, assess its impact on scope/timeline/cost, get stakeholder approval, update relevant documents, and communicate the change to the team."},
    ],
    "Sales": [
        {"q": "What is the sales funnel?",
         "a": "A model showing the stages a customer goes through: Awareness → Interest → Consideration → Intent → Purchase → Loyalty. Each stage has fewer prospects than the one above."},
        {"q": "What is the difference between B2B and B2C sales?",
         "a": "B2B (Business to Business) involves longer sales cycles, multiple decision-makers, and larger deal sizes. B2C (Business to Consumer) has shorter cycles and emotional buying triggers."},
        {"q": "How do you handle a customer objection?",
         "a": "Listen, acknowledge the concern, ask clarifying questions, address it with facts/value, and confirm the resolution. Never argue."},
        {"q": "What is CRM and why is it important?",
         "a": "Customer Relationship Management — software to track interactions with customers. It helps manage pipelines, follow-ups, and sales history in one place."},
        {"q": "What metrics do you track in sales?",
         "a": "Revenue, conversion rate, average deal size, customer acquisition cost, customer lifetime value, churn rate, and monthly/quarterly quota attainment."},
    ],
    "Network Security Engineer": [
        {"q": "What is the difference between IDS and IPS?",
         "a": "IDS (Intrusion Detection System) detects and alerts on suspicious activity. IPS (Intrusion Prevention System) detects AND automatically blocks the threat."},
        {"q": "What is a firewall and how does it work?",
         "a": "A firewall monitors and controls incoming/outgoing network traffic based on security rules. It creates a barrier between trusted internal networks and untrusted external ones."},
        {"q": "What is penetration testing?",
         "a": "Ethical hacking — deliberately attacking a system with permission to find vulnerabilities before malicious hackers do."},
        {"q": "What is the CIA triad?",
         "a": "The three core principles of security: Confidentiality (only authorized access), Integrity (data is accurate and unmodified), Availability (systems are accessible when needed)."},
        {"q": "What is SSL/TLS?",
         "a": "SSL/TLS are protocols that encrypt data transmitted over a network (e.g., HTTPS). TLS is the modern, more secure version of SSL."},
    ],
}

# ----------------------------------------------------------------
# Suggested skills to add per role (for the "Improve Your Resume" section)
# ----------------------------------------------------------------
SUGGESTED_SKILLS = {
    "Python Developer":          ["FastAPI", "Docker", "PostgreSQL", "Redis", "AWS Lambda"],
    "Data Science":              ["PyTorch", "MLflow", "Airflow", "dbt", "Streamlit"],
    "Web Designing":             ["Figma", "After Effects", "Webflow", "GSAP", "Accessibility (WCAG)"],
    "Java Developer":            ["Spring Cloud", "Kafka", "Redis", "Kubernetes", "GraphQL"],
    "DevOps Engineer":           ["ArgoCD", "Istio", "Vault by HashiCorp", "Datadog", "Pulumi"],
    "HR":                        ["SAP SuccessFactors", "Workday", "People Analytics", "DEI Strategy"],
    "Testing":                   ["Playwright", "k6 Performance Testing", "TestRail", "Zephyr", "BDD"],
    "Automation Testing":        ["Playwright", "RestAssured", "Allure Reports", "k6", "Pact (Contract Testing)"],
    "Database":                  ["TimescaleDB", "ClickHouse", "dbt", "Liquibase", "Vector Databases"],
    "Network Security Engineer": ["SOAR platforms", "Zero Trust Architecture", "Cloud Security", "OSINT"],
    "Mechanical Engineer":       ["MATLAB", "ANSYS Fluent", "PTC Creo", "GD&T", "Additive Manufacturing"],
    "Civil Engineer":            ["BIM 360", "Tekla Structures", "Infraworks", "Traffic Engineering"],
    "Electrical Engineering":    ["Power Electronics", "IoT", "FPGA", "Embedded Linux", "EtherCAT"],
    "Blockchain":                ["Zero-Knowledge Proofs", "Layer 2 Solutions", "Rust", "Cosmos SDK"],
    "DotNet Developer":          ["Blazor WebAssembly", "MAUI", "gRPC", "OpenTelemetry", "Minimal APIs"],
    "Hadoop":                    ["Apache Flink", "Delta Lake", "Databricks", "Apache Iceberg"],
    "ETL Developer":             ["Apache Airflow", "dbt", "Fivetran", "Spark Structured Streaming"],
    "Operations Manager":        ["Power BI", "Tableau", "OKR Framework", "Lean Six Sigma Black Belt"],
    "Business Analyst":          ["Power Automate", "Alteryx", "Agile Coaching", "BPMN", "Design Thinking"],
    "SAP Developer":             ["SAP BTP", "SAP Integration Suite", "CAP Framework", "RAP"],
    "Sales":                     ["HubSpot", "Account-Based Marketing", "LinkedIn Sales Navigator", "Negotiation"],
    "Advocate":                  ["Arbitration", "ADR Methods", "Legal Tech Tools", "Data Privacy Law"],
    "Arts":                      ["Procreate", "Blender 3D", "Motion Graphics", "NFT Creation"],
    "Health and fitness":        ["Sports Psychology", "Corrective Exercise", "Telehealth", "Wearables"],
    "PMO":                       ["OKRs", "SAFe Agile", "Power BI Dashboards", "Benefit Realization"],
}
