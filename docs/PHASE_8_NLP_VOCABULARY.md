# IRIS Phase 8 — Natural Language Query Vocabulary & Specification

> **Document Status**: Phase 8 Step 2 Final Specification (Corrected)  
> **Authoritative Source**: IRIS Phase 7 Frozen Implementation (`app/utils/taxonomy.py`, `app/services/resource_service.py`, `app/database/seed_subjects.py`, `data/subjects.txt`, `data/resources.csv`)

---

## 1. Purpose & Scope

This document defines the complete vocabulary, entity mappings, query grammar, field requirements, ambiguity resolution rules, and classification logic for the **IRIS Phase 8 Natural Language Processing (NLP)** query subsystem.

### Key Principles & Constraints
1. **Step 2 Deliverable Only**: This document and its accompanying data dictionary specification (`app/nlp/vocabulary.py`) provide the authoritative vocabulary definition. No NLP processor, parser runtime, or Telegram Search state is executed or integrated in this step.
2. **Zero Modification to Phase 7**: The existing Phase 7 deterministic button navigation, PostgreSQL database schema, resource metadata, file retrieval services, and Telegram handlers remain strictly frozen and untouched.
3. **No Guessing**: The NLP processor must resolve user queries into deterministic parameters matching the existing database schema. If required fields are ambiguous or missing, the system must not guess.

---

## 2. Canonical Resource Taxonomy

Derived from `app/utils/taxonomy.py`, the system supports 6 primary categories with fixed hierarchical subcategories and sub-subcategories.

| Category | Subcategory | Sub-Subcategory | Supported Parameters |
| :--- | :--- | :--- | :--- |
| **Question Papers** | `Semester Examination` | *(none)* | `semester`, `subject_id`, `year` |
| | `Internal Examination` | `First Internal`, `Second Internal` | `semester`, `subject_id`, `year`, `internal_exam` |
| | `Sample Papers` | *(none)* | `semester`, `subject_id` |
| **Notes** | *(none)* | *(none)* | `semester`, `subject_id`, `module` (1-5) |
| **Lab Manuals** | `Record Samples` | *(none)* | `semester`, `subject_id` |
| | `Lab Question Papers` | *(none)* | `semester`, `subject_id`, `year` |
| | `Viva Questions` | *(none)* | `semester`, `subject_id` |
| | `Micro Projects` | *(none)* | `semester`, `subject_id` |
| **Projects** | `Mini Project` | `Abstract Template`<br>`Title Presentation Template`<br>`Final Presentation Template`<br>`Project Report Template` | `subcategory`, `sub_subcategory` *(year is incidental metadata)* |
| | `Main Project` | `Abstract Template`<br>`Title Presentation Template`<br>`Final Presentation Template`<br>`Project Report Template` | `subcategory`, `sub_subcategory` *(year is incidental metadata)* |
| **Reference Materials** | `Bridge Course` | `Previous Year Papers`<br>`Sample Papers`<br>`Syllabus` | `sub_subcategory`, `year` (only for `Previous Year Papers`) |
| | `Micro Project Reports` | *(none)* | `subcategory` |
| | `Internship Reports` | *(none)* | `subcategory` |
| | `Internship Presentations` | *(none)* | `subcategory` |
| | `Syllabus & Academic Guide` | *(none)* | `subcategory` |
| **Placement Materials**| `Aptitude` | *(none)* | `subcategory` |
| | `Technical` | *(none)* | `subcategory` |
| | `HR Interview` | *(none)* | `subcategory` |
| | `Resume Templates` | *(none)* | `subcategory` |

---

## 3. Canonical Subject Catalogue (31 Entries Across S1-S4)

The canonical subject catalogue is derived from `data/subjects.txt` and PostgreSQL `subjects` (`id`, `semester`, `subject_code`, `subject_name`). It contains **31 total entries** (8 in S1, 9 in S2, 11 in S3, 3 in S4).

### Semester 1 (8 Entries)
* **M24CA1C101**: Mathematical Foundations of Computing &Statistical Approaches
* **M24CA1C102**: Digital Fundamentals and Computer Architecture
* **M24CA1C103**: Advanced Software Engineering
* **M24CA1C104**: Advanced Data Structures
* **M24CA1B105**: Web Development Lab
* **M24CA1L106**: Programming Lab
* **M24CA1L107**: Data Structures Lab
* **M24CA1N108**: Research Methodology and Publication Ethics

### Semester 2 (9 Entries)
* **M24CA1C201**: Advanced Computer Networks
* **M24CA1C202**: Advanced Database Management System
* **M24CA1C203**: Advanced Operating Systems
* **M24CA1E204B**: Data Visualization and Predictive Analytics (Elective 1)
* **M24CA1E204D**: Cloud Computing (Elective 1)
* **M24CA1B205**: Object Oriented Programming Lab
* **M24CA1L206**: Advanced Database Lab
* **M24CA1L207**: Operating Systems Lab
* **M24CA1N208**: Personality Development through Life Enlightenment Skills

### Semester 3 (11 Entries)
* **M24CA1C301**: Data Science and Machine Learning
* **M24CA1C302**: Design and Analysis of Algorithms
* **M24CA1E303A**: Artificial Intelligence (Elective 2)
* **M24CA1E303D**: Big Data Management and Analytics (Elective 2)
* **M24CA1E304A**: Deep Learning (Elective 3)
* **M24CA1E304D**: Cloud Computing with AWS/ Azure/ Google Cloud Platform (Elective 3)
* **M24CA1B305**: Mobile Applications Development Lab
* **M24CA1L306**: Data Science Lab
* **M24CA1M307**: M24CA1M307 *(Special Project Entry)*
* **M24CA1I309**: M24CA1I309 *(Special Internship Entry)*
* **M24CA1N308**: Professional Ethics & Human Values

### Semester 4 (3 Entries)
* **M24CA1S402**: Seminar
* **MOOC Course**: MOOC Course
* **M24CA1P401**: M24CA1P401 *(Special Main Project Entry)*

> **Special Subject / Project Entries Mapping Note**:  
> In the PostgreSQL database and source data, `M24CA1M307`, `M24CA1I309`, and `M24CA1P401` are stored using their exact course codes. For human-readable NLP processing, student queries using `"Mini-Project"`, `"Internship"`, and `"Main Project"` resolve to these NLP concepts. However, these human-readable concepts must **NOT** silently replace or modify the underlying database identifiers or subject table records.

---

## 4. Subject Aliases Mapping

Controlled alias list mapping common student natural language expressions to canonical subject records:

| Subject Code | Canonical Subject Name | Safe Natural Language Aliases |
| :--- | :--- | :--- |
| `M24CA1C101` | Mathematical Foundations of Computing &Statistical Approaches | `mfc`, `mfcsa`, `math`, `maths`, `mathematical foundations` |
| `M24CA1C102` | Digital Fundamentals and Computer Architecture | `dfca`, `digital fundamentals`, `computer architecture` |
| `M24CA1C103` | Advanced Software Engineering | `ase`, `software engineering`, `adv software eng` |
| `M24CA1C104` | Advanced Data Structures | `ads`, `advanced data structures` *(note: "data structures" collides with DS Lab)* |
| `M24CA1B105` | Web Development Lab | `web lab`, `web dev lab`, `web development lab` |
| `M24CA1L106` | Programming Lab | `programming lab`, `c lab`, `prog lab` |
| `M24CA1L107` | Data Structures Lab | `ds lab s1`, `data structures lab` |
| `M24CA1N108` | Research Methodology and Publication Ethics | `rm`, `rmpe`, `research methodology` |
| `M24CA1C201` | Advanced Computer Networks | `acn`, `computer networks`, `networks`, `networking` |
| `M24CA1C202` | Advanced Database Management System | `adbms`, `advanced dbms`, `advanced database management system` |
| `M24CA1C203` | Advanced Operating Systems | `aos`, `advanced operating systems` |
| `M24CA1E204B` | Data Visualization and Predictive Analytics | `dv`, `dvpa`, `data visualization`, `predictive analytics` |
| `M24CA1E204D` | Cloud Computing | `cloud computing s2` *(note: "cloud" collides with AWS Cloud S3)* |
| `M24CA1B205` | Object Oriented Programming Lab | `oop lab`, `java lab`, `object oriented lab` |
| `M24CA1L206` | Advanced Database Lab | `adbms lab`, `advanced database lab` |
| `M24CA1L207` | Operating Systems Lab | `os lab`, `operating systems lab` |
| `M24CA1N208` | Personality Development through Life Enlightenment Skills | `pdles`, `personality development` |
| `M24CA1C301` | Data Science and Machine Learning | `dsml`, `machine learning`, `ml` |
| `M24CA1C302` | Design and Analysis of Algorithms | `daa`, `algorithms`, `algo`, `design and analysis of algorithms` |
| `M24CA1E303A` | Artificial Intelligence | `ai`, `artificial intelligence` |
| `M24CA1E303D` | Big Data Management and Analytics | `big data`, `bdma`, `big data analytics` |
| `M24CA1E304A` | Deep Learning | `dl`, `deep learning` |
| `M24CA1E304D` | Cloud Computing with AWS/ Azure/ Google Cloud Platform | `aws`, `aws cloud`, `gcp`, `azure cloud`, `cloud aws` |
| `M24CA1B305` | Mobile Applications Development Lab | `mad lab`, `mobile lab`, `android lab`, `mobile app lab` |
| `M24CA1L306` | Data Science Lab | `data science lab`, `ds lab s3` |
| `M24CA1N308` | Professional Ethics & Human Values | `pehv`, `professional ethics`, `ethics` |

---

## 5. Attribute & Category Alias Controlled Vocabulary

### Resource Categories & Subcategories
* **Question Papers**: `qp`, `qps`, `question paper`, `question papers`, `previous paper`, `previous year paper`, `old paper`, `exam paper`
  * **Semester Examination**: `sem exam`, `semester exam`, `regular exam`, `university exam`, `final exam`
  * **Internal Examination**: `internal`, `internals`, `internal exam`, `series test`, `sessional`
    * **First Internal**: `first internal`, `internal 1`, `series 1`, `1st internal`
    * **Second Internal**: `second internal`, `internal 2`, `series 2`, `2nd internal`
  * **Sample Papers**: `sample paper`, `model paper`, `sample qp`, `model qp`
* **Notes**: `notes`, `study material`, `lecture notes`, `handwritten notes`, `class notes`, `module notes`
* **Lab Manuals**: `lab manual`, `lab manuals`, `lab record`, `lab qp`, `viva questions`
  * **Record Samples**: `record`, `record sample`, `lab record format`
  * **Lab Question Papers**: `lab qp`, `lab question paper`, `lab exam paper`
  * **Viva Questions**: `viva`, `viva questions`, `viva voice`
  * **Micro Projects**: `micro project lab`, `lab micro project`
* **Projects**: `project`, `projects`, `project template`, `mini project`, `main project`
  * **Mini Project**: `mini project`, `mini-project`
  * **Main Project**: `main project`, `major project`
  * **Templates**:
    * `Abstract Template`: `abstract`, `synopsis`, `abstract template`
    * `Title Presentation Template`: `title ppt`, `zeroth ppt`, `title presentation`
    * `Final Presentation Template`: `final ppt`, `final presentation`
    * `Project Report Template`: `project report`, `documentation`, `report template`
* **Reference Materials**: `reference`, `reference material`, `bridge course`, `internship report`, `internship presentation`
  * **Bridge Course**: `bridge course`
    * `Previous Year Papers`: `bridge pyq`, `bridge previous paper`
    * `Sample Papers`: `bridge sample paper`
    * `Syllabus`: `bridge syllabus`
  * **Internship Reports**: `internship report`, `internship documentation`
  * **Internship Presentations**: `internship ppt`, `internship presentation`
  * **Syllabus & Academic Guide**: `academic guide`, `curriculum`, `KTU syllabus`
* **Placement Materials**: `placement`, `placements`, `aptitude`, `technical interview`, `hr interview`, `resume`
  * **Aptitude**: `aptitude`, `quant`, `reasoning`
  * **Technical**: `technical`, `coding questions`, `tech interview`
  * **HR Interview**: `hr`, `hr interview`, `behavioural interview`
  * **Resume Templates**: `resume`, `cv`, `resume template`, `cv format`

### Semester Expressions
* **1**: `s1`, `sem 1`, `sem-1`, `semester 1`, `first semester`, `1st sem`
* **2**: `s2`, `sem 2`, `sem-2`, `semester 2`, `second semester`, `2nd sem`
* **3**: `s3`, `sem 3`, `sem-3`, `semester 3`, `third semester`, `3rd sem`
* **4**: `s4`, `sem 4`, `sem-4`, `semester 4`, `fourth semester`, `4th sem`

### Module Expressions (Only applicable to Notes)
* **1**: `mod 1`, `m1`, `module 1`, `module one`
* **2**: `mod 2`, `m2`, `module 2`, `module two`
* **3**: `mod 3`, `m3`, `module 3`, `module three`
* **4**: `mod 4`, `m4`, `module 4`, `module four`
* **5**: `mod 5`, `m5`, `module 5`, `module five`

---

## 6. Year Rules & Contextual Resolution

1. **Four-Digit Years**:
   * Valid 4-digit numbers in the range `2000-2099` (e.g., `2024`, `2025`) are interpreted as `year`.
   * A year is ONLY valid as a searchable retrieval parameter for:
     - `Question Papers -> Semester Examination`
     - `Question Papers -> Internal Examination`
     - `Lab Manuals -> Lab Question Papers`
     - `Reference Materials -> Bridge Course -> Previous Year Papers`
   * *Project Year Note*: In `resource_service.py`, `get_projects_resources` queries exclusively by `subcategory` and `sub_subcategory`. A year present in a project request is recognized as incidental query metadata only and is **NOT** passed as a database retrieval parameter.
2. **Contextual Numbers**:
   * Isolated numbers `1-5` without explicitly attached keywords ("module", "sem", "internal") are ambiguous.
   * "DBMS 2" -> **AMBIGUOUS** (could mean Semester 2 or Module 2).
   * "DBMS module 2" -> `module: 2`
   * "S2 DBMS" -> `semester: 2`

---

## 7. Natural Language Query Grammar Patterns

The NLP processor will accept order-flexible query patterns and normalize them into a single target parameter structure:

* `[Semester] [Subject] [Module] [Category]`  
  *Example*: `"S3 DBMS module 2 notes"`
* `[Subject] [Semester] [Module] [Category]`  
  *Example*: `"DBMS S3 module 2 notes"`
* `[Category] [Module] for [Subject] in [Semester]`  
  *Example*: `"Notes module 2 for DBMS in sem 3"`
* `[Natural Request Prefix] [Module] [Category] for [Subject] in [Semester]`  
  *Example*: `"I need module 2 notes for DBMS in third semester"`
* `[Question Prefix] [Semester] [Subject] [Module] [Category]?`  
  *Example*: `"Can you give me third semester DBMS module 2 notes?"`

All variations above resolve to the identical payload:
```json
{
  "category": "Notes",
  "semester": 3,
  "subject_id": 10,
  "module": 2
}
```

---

## 8. Required & Optional Parameter Matrix

| Category | Subcategory | Required Fields | Optional Fields | N/A Fields |
| :--- | :--- | :--- | :--- | :--- |
| **Question Papers** | `Semester Examination` | `semester`, `subject_id` | `year` | `module`, `internal_exam` |
| | `Internal Examination` | `semester`, `subject_id`, `year`, `internal_exam` | *(none)* | `module` |
| | `Sample Papers` | `semester`, `subject_id` | *(none)* | `year`, `module`, `internal_exam` |
| **Notes** | *(none)* | `semester`, `subject_id`, `module` | *(none)* | `year`, `subcategory`, `internal_exam` |
| **Lab Manuals** | `Record Samples` | `semester`, `subject_id` | *(none)* | `year`, `module`, `internal_exam` |
| | `Lab Question Papers` | `semester`, `subject_id`, `year` | *(none)* | `module`, `internal_exam` |
| | `Viva Questions` | `semester`, `subject_id` | *(none)* | `year`, `module`, `internal_exam` |
| | `Micro Projects` | `semester`, `subject_id` | *(none)* | `year`, `module`, `internal_exam` |
| **Projects** | `Mini Project` | `subcategory`, `sub_subcategory` | *(none)* *(year is incidental)* | `semester`, `subject_id`, `module`, `internal_exam` |
| | `Main Project` | `subcategory`, `sub_subcategory` | *(none)* *(year is incidental)* | `semester`, `subject_id`, `module`, `internal_exam` |
| **Reference Materials** | `Bridge Course` | `sub_subcategory` | `year` (if `Previous Year Papers`) | `semester`, `subject_id`, `module` |
| | `Micro Project Reports` / `Internship Reports` / `Internship Presentations` / `Syllabus & Academic Guide` | `subcategory` | *(none)* | `semester`, `subject_id`, `year`, `module` |
| **Placement Materials**| `Aptitude` / `Technical` / `HR Interview` / `Resume Templates` | `subcategory` | *(none)* | `semester`, `subject_id`, `year`, `module` |

---

## 9. Ambiguity Rules & Alias Collision Resolution

The NLP processor **MUST** return `AMBIGUOUS` and refuse to guess when an alias or query term collides across multiple canonical entities without explicit context:

### Key Alias Collision Rules
1. **`ds lab`**: Collides between `M24CA1L107` (*Data Structures Lab*, Sem 1) and `M24CA1L306` (*Data Science Lab*, Sem 3).  
   → Must provide semester context (`S1` or `S3`), otherwise returns `AMBIGUOUS`.
2. **`cloud`**: Collides between `M24CA1E204D` (*Cloud Computing*, Sem 2) and `M24CA1E304D` (*Cloud Computing with AWS/Azure/GCP*, Sem 3).  
   → Must provide semester or AWS context, otherwise returns `AMBIGUOUS`.
3. **`data`**: Collides across MFC (`M24CA1C101`), ADS (`M24CA1C104`), DS Lab (`M24CA1L107`), ADBMS (`M24CA1C202`), DVPA (`M24CA1E204B`), ADBMS Lab (`M24CA1L206`), DSML (`M24CA1C301`), Big Data (`M24CA1E303D`), and Data Science Lab (`M24CA1L306`).  
   → Returns `AMBIGUOUS` if unqualified.
4. **`database`**: Collides between ADBMS (`M24CA1C202`) and ADBMS Lab (`M24CA1L206`).  
   → Returns `AMBIGUOUS` unless theory vs lab context is specified.
5. **`project`**: Collides between Mini Project (`Projects`), Main Project (`Projects`), Micro Projects (`Lab Manuals`), and Micro Project Reports (`Reference Materials`).  
   → Returns `AMBIGUOUS` unless specific subcategory is qualified.
6. **`syllabus`**: Collides between `Reference Materials -> Bridge Course -> Syllabus` and `Reference Materials -> Syllabus & Academic Guide`.  
   → Returns `AMBIGUOUS` without explicit subcategory context.

*Core Rule*: When multiple plausible canonical entities exist and the query lacks context to choose one, NLP **MUST NEVER GUESS** by picking the first dictionary entry.

---

## 10. Incomplete Query Rules

A query is classified as `INCOMPLETE` when the intent and subject/category are recognized, but mandatory parameters required for database retrieval are missing:

* **Query**: `"DBMS notes"` -> Missing `semester` and `module`.
* **Query**: `"question paper for ACN"` -> Missing `subcategory` (Semester Exam, Internal, or Sample Paper).
* **Query**: `"internal exam qp for OS"` -> Missing `year` and `internal_exam` (First or Second Internal).

---

## 11. Unsupported Query Rules

Requests classified as `UNSUPPORTED` are recognized as user intentions outside IRIS's database retrieval purpose. The system will NOT perform a PostgreSQL query for:

* Document summarization: `"summarize this pdf"`
* Academic topic explanation: `"explain database normalization"`
* Code generation: `"write a python program for binary search"`
* Exam question solving: `"solve question 3 from 2024 QP"`
* General web search: `"search google for interview questions"`

---

## 12. No-Resource Query Rules

Conversational greetings, bot metadata queries, or social interactions return `NO_RESOURCE_QUERY` and do NOT hit PostgreSQL:

* `"hello"`, `"hi"`, `"hey"`
* `"how are you?"`
* `"thank you"`, `"thanks"`
* `"who made you?"`

---

## 13. Multiple-Request Rule

If a single user message contains multiple resource requests:  
*Example*: `"S3 DBMS notes and S4 OS question paper"`

The system **MUST process ONLY the first recognized resource request** (`"S3 DBMS notes"`). Multi-query parsing or batch execution is strictly prohibited.

---

## 14. Existing Data Inconsistencies (Documented As-Is)

The following discrepancies exist in the seed dataset and are preserved without modification:

1. **Subject Name Mismatch**: In `resources.csv`, lines 27-31, subject name for code `M24CA1C202` is listed as `"Advanced DBMS"`, whereas in `data/subjects.txt` line 16, it is `"Advanced Database Management System"`.
2. **Trailing Whitespace**: In `data/subjects.txt` line 29, the subject name has trailing whitespace before parenthesis: `"Artificial Intelligence ( Elective 2)"`.
3. **Standalone Project Codes**: In `data/subjects.txt` lines 46, 50, 54, project codes `M24CA1M307`, `M24CA1I309`, and `M24CA1P401` appear as both code and name without descriptive text, mapped to semesters via `SPECIAL_SEMESTERS` in `seed_subjects.py`.
4. **Lab Manual Subject Mapping**: In `resources.csv` lines 275-278, `Lab Manuals` has entries for `M24CA1N108` (`Research Methodology`), which is listed under S1 as a theory/ethics course.
5. **Project Template Semester/Subject Nullity**: In `resources.csv` lines 311-326, project templates have `Year` populated (`2024`, `2025`), but `Semester` and `Subject_Code` are `NULL`.

---

## 15. Explicit Phase 8 Boundaries

* **NO NLP Runtime Execution**: No parser logic or NLP model is active in Step 2.
* **NO Search Integration**: The Telegram Search button callback handler remains unchanged.
* **NO DB Schema Modification**: Table schemas and constraints remain 100% untouched.
