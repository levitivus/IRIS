"""
app/nlp/vocabulary.py

Phase 8 Step 2 — IRIS NLP Data Dictionary & Controlled Vocabulary Specification (Corrected).

This module contains static data structures, mappings, and controlled vocabulary
definitions for the future Phase 8 NLP query processor.

CRITICAL CONSTRAINTS:
- Contains data structures and configuration ONLY.
- NO NLP processor runtime or execution logic.
- NOT imported by the main application or any running Phase 7 handlers.
- Zero external runtime dependencies.
"""

from typing import Any, Dict, List

# ==============================================================================
# 1. CANONICAL CATEGORIES & TAXONOMY STRUCTURE
# ==============================================================================

CANONICAL_CATEGORIES: List[str] = [
    "Question Papers",
    "Notes",
    "Lab Manuals",
    "Projects",
    "Reference Materials",
    "Placement Materials",
]

TAXONOMY_HIERARCHY: Dict[str, Dict[str, Any]] = {
    "Question Papers": {
        "subcategories": ["Semester Examination", "Internal Examination", "Sample Papers"],
        "sub_subcategories": {
            "Internal Examination": ["First Internal", "Second Internal"]
        },
    },
    "Notes": {
        "subcategories": [],
        "modules": [1, 2, 3, 4, 5],
    },
    "Lab Manuals": {
        "subcategories": [
            "Record Samples",
            "Lab Question Papers",
            "Viva Questions",
            "Micro Projects",
        ]
    },
    "Projects": {
        "subcategories": ["Mini Project", "Main Project"],
        "sub_subcategories": {
            "Mini Project": [
                "Abstract Template",
                "Title Presentation Template",
                "Final Presentation Template",
                "Project Report Template",
            ],
            "Main Project": [
                "Abstract Template",
                "Title Presentation Template",
                "Final Presentation Template",
                "Project Report Template",
            ],
        },
    },
    "Reference Materials": {
        "subcategories": [
            "Bridge Course",
            "Micro Project Reports",
            "Internship Reports",
            "Internship Presentations",
            "Syllabus & Academic Guide",
        ],
        "sub_subcategories": {
            "Bridge Course": ["Previous Year Papers", "Sample Papers", "Syllabus"]
        },
    },
    "Placement Materials": {
        "subcategories": ["Aptitude", "Technical", "HR Interview", "Resume Templates"]
    },
}


# ==============================================================================
# 2. CANONICAL SUBJECT CATALOGUE (31 ENTRIES ACROSS S1-S4)
# ==============================================================================

CANONICAL_SUBJECTS: List[Dict[str, Any]] = [
    # Semester 1 (8 entries)
    {"code": "M24CA1C101", "name": "Mathematical Foundations of Computing &Statistical Approaches", "semester": 1},
    {"code": "M24CA1C102", "name": "Digital Fundamentals and Computer Architecture", "semester": 1},
    {"code": "M24CA1C103", "name": "Advanced Software Engineering", "semester": 1},
    {"code": "M24CA1C104", "name": "Advanced Data Structures", "semester": 1},
    {"code": "M24CA1B105", "name": "Web Development Lab", "semester": 1},
    {"code": "M24CA1L106", "name": "Programming Lab", "semester": 1},
    {"code": "M24CA1L107", "name": "Data Structures Lab", "semester": 1},
    {"code": "M24CA1N108", "name": "Research Methodology and Publication Ethics", "semester": 1},
    # Semester 2 (9 entries)
    {"code": "M24CA1C201", "name": "Advanced Computer Networks", "semester": 2},
    {"code": "M24CA1C202", "name": "Advanced Database Management System", "semester": 2},
    {"code": "M24CA1C203", "name": "Advanced Operating Systems", "semester": 2},
    {"code": "M24CA1E204B", "name": "Data Visualization and Predictive Analytics", "semester": 2},
    {"code": "M24CA1E204D", "name": "Cloud Computing", "semester": 2},
    {"code": "M24CA1B205", "name": "Object Oriented Programming Lab", "semester": 2},
    {"code": "M24CA1L206", "name": "Advanced Database Lab", "semester": 2},
    {"code": "M24CA1L207", "name": "Operating Systems Lab", "semester": 2},
    {"code": "M24CA1N208", "name": "Personality Development through Life Enlightenment Skills", "semester": 2},
    # Semester 3 (11 entries)
    {"code": "M24CA1C301", "name": "Data Science and Machine Learning", "semester": 3},
    {"code": "M24CA1C302", "name": "Design and Analysis of Algorithms", "semester": 3},
    {"code": "M24CA1E303A", "name": "Artificial Intelligence", "semester": 3},
    {"code": "M24CA1E303D", "name": "Big Data Management and Analytics", "semester": 3},
    {"code": "M24CA1E304A", "name": "Deep Learning", "semester": 3},
    {"code": "M24CA1E304D", "name": "Cloud Computing with AWS/ Azure/ Google Cloud Platform", "semester": 3},
    {"code": "M24CA1B305", "name": "Mobile Applications Development Lab", "semester": 3},
    {"code": "M24CA1L306", "name": "Data Science Lab", "semester": 3},
    {"code": "M24CA1M307", "name": "M24CA1M307", "semester": 3, "is_special_entry": True, "nlp_concept": "Mini-Project"},
    {"code": "M24CA1I309", "name": "M24CA1I309", "semester": 3, "is_special_entry": True, "nlp_concept": "Internship"},
    {"code": "M24CA1N308", "name": "Professional Ethics & Human Values", "semester": 3},
    # Semester 4 (3 entries)
    {"code": "M24CA1S402", "name": "Seminar", "semester": 4},
    {"code": "MOOC Course", "name": "MOOC Course", "semester": 4},
    {"code": "M24CA1P401", "name": "Main Project", "semester": 4, "is_special_entry": True, "nlp_concept": "Main Project"},
]


# ==============================================================================
# 3. CONTROLLED SUBJECT ALIASES
# ==============================================================================

SUBJECT_ALIASES: Dict[str, List[str]] = {
    "M24CA1C101": ["mfc", "mfcsa", "math", "maths", "mathematical foundations", "mathematical foundations of computing"],
    "M24CA1C102": ["dfca", "digital fundamentals", "computer architecture", "digital fundamentals and computer architecture"],
    "M24CA1C103": ["ase", "software engineering", "advanced software engineering"],
    "M24CA1C104": ["ads", "advanced data structures"],  # "data structures" collides with DS Lab
    "M24CA1B105": ["web lab", "web dev lab", "web development lab"],
    "M24CA1L106": ["programming lab", "c lab", "prog lab"],
    "M24CA1L107": ["ds lab s1", "data structures lab"],
    "M24CA1N108": ["rm", "rmpe", "research methodology", "publication ethics"],
    "M24CA1C201": ["acn", "computer networks", "networks", "networking", "advanced computer networks"],
    "M24CA1C202": ["adbms", "advanced dbms", "advanced database management system"],
    "M24CA1C203": ["aos", "advanced operating systems"],
    "M24CA1E204B": ["dv", "dvpa", "data visualization", "predictive analytics"],
    "M24CA1E204D": ["cloud computing s2"],  # "cloud" collides with AWS Cloud S3
    "M24CA1B205": ["oop lab", "java lab", "object oriented programming lab"],
    "M24CA1L206": ["adbms lab", "advanced database lab"],
    "M24CA1L207": ["os lab", "operating systems lab"],
    "M24CA1N208": ["pdles", "personality development"],
    "M24CA1C301": ["dsml", "machine learning", "ml", "data science and machine learning"],
    "M24CA1C302": ["daa", "algorithms", "algo", "design and analysis of algorithms"],
    "M24CA1E303A": ["ai", "artificial intelligence"],
    "M24CA1E303D": ["big data", "bdma", "big data analytics", "big data management"],
    "M24CA1E304A": ["dl", "deep learning"],
    "M24CA1E304D": ["aws", "aws cloud", "gcp", "azure cloud", "cloud aws"],
    "M24CA1B305": ["mad lab", "mobile lab", "android lab", "mobile app lab", "mobile applications development lab"],
    "M24CA1L306": ["data science lab", "ds lab s3"],
    "M24CA1N308": ["pehv", "professional ethics", "ethics", "human values"],
    "M24CA1M307": ["mini project course", "m307"],
    "M24CA1I309": ["internship course", "i309"],
    "M24CA1P401": ["main project course", "p401"],
}

# Alias collision definitions for ambiguity resolution
ALIAS_COLLISIONS: Dict[str, List[str]] = {
    "ds lab": ["M24CA1L107", "M24CA1L306"],  # Data Structures Lab (S1) vs Data Science Lab (S3)
    "cloud": ["M24CA1E204D", "M24CA1E304D"],  # Cloud Computing (S2) vs Cloud Computing AWS (S3)
    "data": ["M24CA1C101", "M24CA1C104", "M24CA1L107", "M24CA1C202", "M24CA1E204B", "M24CA1L206", "M24CA1C301", "M24CA1E303D", "M24CA1L306"],
    "database": ["M24CA1C202", "M24CA1L206"],  # ADBMS theory vs ADBMS Lab
    "project": ["Projects:Mini Project", "Projects:Main Project", "Lab Manuals:Micro Projects", "Reference Materials:Micro Project Reports"],
    "syllabus": ["Reference Materials:Bridge Course:Syllabus", "Reference Materials:Syllabus & Academic Guide"],
}


# ==============================================================================
# 4. CATEGORY & ATTRIBUTE ALIAS MAPPING
# ==============================================================================

CATEGORY_ALIASES: Dict[str, List[str]] = {
    "Question Papers": ["qp", "qps", "question paper", "question papers", "previous paper", "previous year paper", "old paper", "exam paper"],
    "Notes": ["notes", "study material", "lecture notes", "handwritten notes", "class notes", "module notes"],
    "Lab Manuals": ["lab manual", "lab manuals", "lab record", "lab qp", "viva questions"],
    "Projects": ["project", "projects", "project template", "mini project", "main project"],
    "Reference Materials": ["reference", "reference material", "bridge course", "internship report", "internship presentation"],
    "Placement Materials": ["placement", "placements", "aptitude", "technical interview", "hr interview", "resume"],
}

SUBCATEGORY_ALIASES: Dict[str, Dict[str, List[str]]] = {
    "Question Papers": {
        "Semester Examination": ["sem exam", "semester exam", "regular exam", "university exam", "final exam"],
        "Internal Examination": ["internal", "internals", "internal exam", "series test", "sessional"],
        "Sample Papers": ["sample paper", "model paper", "sample qp", "model qp"],
    },
    "Lab Manuals": {
        "Record Samples": ["record", "record sample", "lab record format"],
        "Lab Question Papers": ["lab qp", "lab question paper", "lab exam paper"],
        "Viva Questions": ["viva", "viva questions", "viva voice"],
        "Micro Projects": ["micro project lab", "lab micro project"],
    },
    "Projects": {
        "Mini Project": ["mini project", "mini-project"],
        "Main Project": ["main project", "major project"],
    },
    "Reference Materials": {
        "Bridge Course": ["bridge course"],
        "Micro Project Reports": ["micro project report"],
        "Internship Reports": ["internship report", "internship documentation"],
        "Internship Presentations": ["internship ppt", "internship presentation"],
        "Syllabus & Academic Guide": ["academic guide", "curriculum", "ktu syllabus"],
    },
    "Placement Materials": {
        "Aptitude": ["aptitude", "quant", "reasoning"],
        "Technical": ["technical", "coding questions", "tech interview"],
        "HR Interview": ["hr", "hr interview", "behavioural interview"],
        "Resume Templates": ["resume", "cv", "resume template", "cv format"],
    },
}

SUB_SUBCATEGORY_ALIASES: Dict[str, List[str]] = {
    "First Internal": ["first internal", "internal 1", "series 1", "1st internal"],
    "Second Internal": ["second internal", "internal 2", "series 2", "2nd internal"],
    "Abstract Template": ["abstract", "synopsis", "abstract template"],
    "Title Presentation Template": ["title ppt", "zeroth ppt", "title presentation"],
    "Final Presentation Template": ["final ppt", "final presentation"],
    "Project Report Template": ["project report", "documentation", "report template"],
    "Previous Year Papers": ["bridge pyq", "bridge previous paper"],
    "Sample Papers": ["bridge sample paper"],
    "Syllabus": ["bridge syllabus"],
}

SEMESTER_ALIASES: Dict[int, List[str]] = {
    1: ["s1", "sem 1", "sem-1", "semester 1", "first semester", "1st sem"],
    2: ["s2", "sem 2", "sem-2", "semester 2", "second semester", "2nd sem"],
    3: ["s3", "sem 3", "sem-3", "semester 3", "third semester", "3rd sem"],
    4: ["s4", "sem 4", "sem-4", "semester 4", "fourth semester", "4th sem"],
}

MODULE_ALIASES: Dict[int, List[str]] = {
    1: ["mod 1", "m1", "module 1", "module one"],
    2: ["mod 2", "m2", "module 2", "module two"],
    3: ["mod 3", "m3", "module 3", "module three"],
    4: ["mod 4", "m4", "module 4", "module four"],
    5: ["mod 5", "m5", "module 5", "module five"],
}


# ==============================================================================
# 5. REQUIRED & OPTIONAL PARAMETER MATRIX
# ==============================================================================

FIELD_REQUIREMENTS_MATRIX: Dict[str, Dict[str, Any]] = {
    "Question Papers:Semester Examination": {
        "required": ["semester", "subject_id"],
        "optional": ["year"],
        "na": ["module", "internal_exam"],
    },
    "Question Papers:Internal Examination": {
        "required": ["semester", "subject_id", "year", "internal_exam"],
        "optional": [],
        "na": ["module"],
    },
    "Question Papers:Sample Papers": {
        "required": ["semester", "subject_id"],
        "optional": [],
        "na": ["year", "module", "internal_exam"],
    },
    "Notes": {
        "required": ["semester", "subject_id", "module"],
        "optional": [],
        "na": ["year", "subcategory", "internal_exam"],
    },
    "Lab Manuals:Record Samples": {
        "required": ["semester", "subject_id"],
        "optional": [],
        "na": ["year", "module", "internal_exam"],
    },
    "Lab Manuals:Lab Question Papers": {
        "required": ["semester", "subject_id", "year"],
        "optional": [],
        "na": ["module", "internal_exam"],
    },
    "Lab Manuals:Viva Questions": {
        "required": ["semester", "subject_id"],
        "optional": [],
        "na": ["year", "module", "internal_exam"],
    },
    "Lab Manuals:Micro Projects": {
        "required": ["semester", "subject_id"],
        "optional": [],
        "na": ["year", "module", "internal_exam"],
    },
    "Projects:Mini Project": {
        "required": ["subcategory", "sub_subcategory"],
        "optional": [],  # Year is not a retrieval parameter in get_projects_resources
        "incidental": ["year"],
        "na": ["semester", "subject_id", "module", "internal_exam"],
    },
    "Projects:Main Project": {
        "required": ["subcategory", "sub_subcategory"],
        "optional": [],  # Year is not a retrieval parameter in get_projects_resources
        "incidental": ["year"],
        "na": ["semester", "subject_id", "module", "internal_exam"],
    },
    "Reference Materials:Bridge Course": {
        "required": ["sub_subcategory"],
        "optional": ["year"],  # Valid only for Previous Year Papers
        "na": ["semester", "subject_id", "module"],
    },
    "Reference Materials:Generic": {
        "required": ["subcategory"],
        "optional": [],
        "na": ["semester", "subject_id", "year", "module"],
    },
    "Placement Materials": {
        "required": ["subcategory"],
        "optional": [],
        "na": ["semester", "subject_id", "year", "module"],
    },
}


# ==============================================================================
# 6. QUERY CLASSIFICATION OUTCOMES
# ==============================================================================

CLASSIFICATION_OUTCOMES: List[str] = [
    "VALID",
    "INCOMPLETE",
    "AMBIGUOUS",
    "UNSUPPORTED",
    "NO_RESOURCE_QUERY",
    "ERROR",
]
