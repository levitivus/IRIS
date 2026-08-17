"""
app/nlp/processor.py

Phase 8 Step 3 — Isolated NLP Query Processor for IRIS.

Converts a student's natural-language resource query into a structured NLPResult.
Follows the frozen Step 2 specification defined in app/nlp/vocabulary.py and docs/PHASE_8_NLP_VOCABULARY.md.

CRITICAL CONSTRAINTS:
- ZERO database access (no SQL, no PostgreSQL calls).
- ZERO resource_service access.
- ZERO Telegram API or handler access.
- Pure Python standard library implementation with zero new dependencies.
"""

import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Set

from app.nlp.vocabulary import (
    ALIAS_COLLISIONS,
    CANONICAL_CATEGORIES,
    CANONICAL_SUBJECTS,
    CATEGORY_ALIASES,
    FIELD_REQUIREMENTS_MATRIX,
    MODULE_ALIASES,
    SEMESTER_ALIASES,
    SUB_SUBCATEGORY_ALIASES,
    SUBCATEGORY_ALIASES,
    SUBJECT_ALIASES,
    TAXONOMY_HIERARCHY,
)

logger = logging.getLogger(__name__)


class NLPStatus(str, Enum):
    VALID = "VALID"
    INCOMPLETE = "INCOMPLETE"
    AMBIGUOUS = "AMBIGUOUS"
    UNSUPPORTED = "UNSUPPORTED"
    NO_RESOURCE_QUERY = "NO_RESOURCE_QUERY"
    ERROR = "ERROR"


@dataclass
class NLPResult:
    status: NLPStatus
    category: Optional[str] = None
    subcategory: Optional[str] = None
    sub_subcategory: Optional[str] = None
    semester: Optional[int] = None
    subject_code: Optional[str] = None
    subject_name: Optional[str] = None
    module: Optional[int] = None
    year: Optional[int] = None
    internal_exam: Optional[int] = None
    missing_fields: List[str] = field(default_factory=list)
    ambiguous_field: Optional[str] = None
    ambiguous_candidates: List[str] = field(default_factory=list)
    reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Converts result to a dictionary representation."""
        res: Dict[str, Any] = {"status": self.status.value}
        for attr in [
            "category",
            "subcategory",
            "sub_subcategory",
            "semester",
            "subject_code",
            "subject_name",
            "module",
            "year",
            "internal_exam",
            "missing_fields",
            "ambiguous_field",
            "ambiguous_candidates",
            "reason",
        ]:
            val = getattr(self, attr)
            if val:
                res[attr] = val
        return res


# Conversational / social phrases indicating NO_RESOURCE_QUERY
GREETING_PHRASES: Set[str] = {
    "hello",
    "hi",
    "hey",
    "greetings",
    "good morning",
    "good afternoon",
    "good evening",
    "how are you",
    "how r u",
    "tell me a joke",
    "what is the weather",
    "weather",
    "who made you",
    "who created you",
    "thanks",
    "thank you",
    "thx",
    "who are you",
    "what can you do",
    "bye",
    "goodbye",
}

# Action verbs / keywords indicating UNSUPPORTED request intents
UNSUPPORTED_PATTERNS: List[str] = [
    r"\bsummariz",
    r"\bsummary\b",
    r"\bexplain\b",
    r"\bsolve\b",
    r"\bwrite\s+(?:a\s+)?(?:python|c|code|program|script)\b",
    r"\bgenerate\s+notes\b",
    r"\bsearch\s+google\b",
    r"\bgoogle\s+search\b",
    r"\bhow\s+to\b",
    r"\banswer\s+(?:this|question)\b",
]


def normalize_text(text: str) -> str:
    """Normalizes query string into lowercase, replacing hyphen/slash separators and trimming extra whitespace."""
    if not text:
        return ""
    normalized = text.lower()
    # Replace hyphen or slash inside terms (e.g. sem-3 -> sem 3, mod-2 -> mod 2, mini-project -> mini project)
    normalized = re.sub(r"([a-z0-9]+)[-/]([a-z0-9]+)", r"\1 \2", normalized)
    # Replace punctuation with spaces
    normalized = re.sub(r"[^\w\s]", " ", normalized)
    # Collapse whitespace
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


def _split_multiple_requests(query: str) -> str:
    """If multiple queries are connected by 'and', 'also', ';', returns only the first query segment."""
    # Look for conjunction splits like " and ", " also ", ";"
    parts = re.split(r"\b(?:and|also|plus)\b|;", query, flags=re.IGNORECASE)
    if len(parts) > 1:
        # Return first non-empty segment
        first_part = parts[0].strip()
        if len(first_part) > 2:
            return first_part
    return query


def _extract_semester(text: str) -> Optional[int]:
    """Extracts semester integer (1-4) from normalized text."""
    # Pattern 1: s1, s2, sem 1, sem-1, semester 1
    match = re.search(r"\b(?:s|sem|semester)\s*([1-4])\b", text)
    if match:
        return int(match.group(1))

    # Pattern 2: 1st sem, 2nd semester, 3rd sem
    match = re.search(r"\b([1-4])(?:st|nd|rd|th)\s*(?:sem|semester)\b", text)
    if match:
        return int(match.group(1))

    # Pattern 3: word semesters
    words = {
        "first": 1, "1st": 1,
        "second": 2, "2nd": 2,
        "third": 3, "3rd": 3,
        "fourth": 4, "4th": 4,
    }
    for word, sem in words.items():
        if re.search(rf"\b{word}\s*(?:sem|semester)\b", text):
            return sem

    # Pattern 4: standalone s1, s2, s3, s4
    match = re.search(r"\bs([1-4])\b", text)
    if match:
        return int(match.group(1))

    return None


def _extract_module(text: str) -> Optional[int]:
    """Extracts module integer (1-5) from normalized text."""
    # Pattern 1: mod 1, module 2, m3
    match = re.search(r"\b(?:mod|module)\s*([1-5])\b", text)
    if match:
        return int(match.group(1))

    match = re.search(r"\bm\s*([1-5])\b", text)
    if match:
        return int(match.group(1))

    # Pattern 2: module one, module two, etc.
    word_mods = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}
    for word, mod in word_mods.items():
        if re.search(rf"\bmodule\s*{word}\b", text):
            return mod

    return None


def _extract_year(text: str) -> Optional[int]:
    """Extracts 4-digit year (2000-2099) from text."""
    match = re.search(r"\b(20[0-9]{2})\b", text)
    if match:
        return int(match.group(1))
    return None


def _extract_internal_exam(text: str) -> Optional[int]:
    """Extracts internal exam integer (1 or 2) from text."""
    if re.search(r"\b(?:first|1st|1)\s*(?:internal|series)\b", text) or re.search(r"\bseries\s*(?:test\s*)?1\b", text):
        return 1
    if re.search(r"\b(?:second|2nd|2)\s*(?:internal|series)\b", text) or re.search(r"\bseries\s*(?:test\s*)?2\b", text):
        return 2
    return None


def _extract_category_and_subcategories(
    text: str,
) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Extracts (category, subcategory, sub_subcategory) based on vocabulary aliases."""
    cat: Optional[str] = None
    subcat: Optional[str] = None
    sub_subcat: Optional[str] = None

    # Check Sub-subcategories first
    for sub_sub_name, aliases in SUB_SUBCATEGORY_ALIASES.items():
        for alias in aliases:
            if re.search(rf"\b{re.escape(alias)}\b", text):
                sub_subcat = sub_sub_name
                break
        if sub_subcat:
            break

    # Check Subcategories
    for c_name, sub_map in SUBCATEGORY_ALIASES.items():
        for s_name, aliases in sub_map.items():
            for alias in aliases:
                if re.search(rf"\b{re.escape(alias)}\b", text):
                    cat = c_name
                    subcat = s_name
                    break
            if subcat:
                break
        if subcat:
            break

    # Check Categories if not inferred from subcategory
    if not cat:
        for c_name, aliases in CATEGORY_ALIASES.items():
            for alias in aliases:
                if re.search(rf"\b{re.escape(alias)}\b", text):
                    cat = c_name
                    break
            if cat:
                break

    # Category specific inferences
    if cat == "Question Papers" and not subcat:
        if sub_subcat in ["First Internal", "Second Internal"]:
            subcat = "Internal Examination"
        elif re.search(r"\b(?:internal|internals|series)\b", text):
            subcat = "Internal Examination"
        elif re.search(r"\b(?:sample|model)\b", text):
            subcat = "Sample Papers"
        elif re.search(r"\b(?:sem|semester|regular|university|final)\b", text) or _extract_year(text):
            subcat = "Semester Examination"

    if cat == "Notes":
        subcat = None

    return cat, subcat, sub_subcat


def _resolve_subject(
    text: str, semester_hint: Optional[int], category_hint: Optional[str]
) -> Tuple[Optional[Dict[str, Any]], Optional[str], List[str]]:
    """
    Resolves subject from query text using canonical subjects and aliases.
    Returns: (subject_dict, ambiguous_field_name, ambiguous_candidate_labels)
    """
    # Check for direct subject code matches (e.g. M24CA1C101, m24ca1c202)
    for subj in CANONICAL_SUBJECTS:
        code_lower = subj["code"].lower()
        if re.search(rf"\b{re.escape(code_lower)}\b", text):
            return subj, None, []

    # Check for exact canonical subject name matches
    for subj in CANONICAL_SUBJECTS:
        name_lower = subj["name"].lower()
        if len(name_lower) > 3 and name_lower in text:
            return subj, None, []

    # Check explicit alias collisions first
    # 1. "ds lab" collision
    if re.search(r"\bds\s+lab\b", text):
        if semester_hint == 1 or re.search(r"\bdata\s+structures\b", text):
            return (
                next(s for s in CANONICAL_SUBJECTS if s["code"] == "M24CA1L107"),
                None,
                [],
            )
        elif semester_hint == 3 or re.search(r"\bdata\s+science\b", text):
            return (
                next(s for s in CANONICAL_SUBJECTS if s["code"] == "M24CA1L306"),
                None,
                [],
            )
        else:
            return (
                None,
                "subject",
                [
                    "M24CA1L107 (Data Structures Lab - Sem 1)",
                    "M24CA1L306 (Data Science Lab - Sem 3)",
                ],
            )

    # 2. "cloud" collision
    if re.search(r"\bcloud\b", text) and not re.search(r"\bcloud\s+computing\s+s2\b", text):
        if semester_hint == 2:
            return (
                next(s for s in CANONICAL_SUBJECTS if s["code"] == "M24CA1E204D"),
                None,
                [],
            )
        elif semester_hint == 3 or any(k in text for k in ["aws", "gcp", "azure"]):
            return (
                next(s for s in CANONICAL_SUBJECTS if s["code"] == "M24CA1E304D"),
                None,
                [],
            )
        else:
            return (
                None,
                "subject",
                [
                    "M24CA1E204D (Cloud Computing - Sem 2)",
                    "M24CA1E304D (Cloud Computing with AWS - Sem 3)",
                ],
            )

    # 3. "dbms" / "database" resolution
    if re.search(r"\b(?:dbms|database)\b", text) and not any(k in text for k in ["advanced database", "adbms"]):
        if re.search(r"\blab\b", text) or category_hint == "Lab Manuals":
            return (
                next(s for s in CANONICAL_SUBJECTS if s["code"] == "M24CA1L206"),
                None,
                [],
            )
        else:
            return (
                next(s for s in CANONICAL_SUBJECTS if s["code"] == "M24CA1C202"),
                None,
                [],
            )

    # 4. Unqualified "data" collision across 9 subjects
    if re.search(r"\bdata\b", text) and not any(
        k in text for k in ["data structures", "data visualization", "data science", "big data", "database", "dbms"]
    ):
        return (
            None,
            "subject",
            [
                "M24CA1C101 (MFC)",
                "M24CA1C104 (ADS)",
                "M24CA1L107 (DS Lab S1)",
                "M24CA1C202 (ADBMS)",
                "M24CA1E204B (Data Visualization)",
                "M24CA1L206 (ADBMS Lab)",
                "M24CA1C301 (DSML)",
                "M24CA1E303D (Big Data)",
                "M24CA1L306 (DS Lab S3)",
            ],
        )

    # Expanded Subject Alias Map for common phrasing variations
    EXPANDED_ALIASES = dict(SUBJECT_ALIASES)
    EXPANDED_ALIASES["M24CA1C103"] = list(set(EXPANDED_ALIASES["M24CA1C103"] + ["adv software eng", "software eng", "adv software engineering"]))
    EXPANDED_ALIASES["M24CA1C202"] = list(set(EXPANDED_ALIASES["M24CA1C202"] + ["dbms", "database"]))

    # Match aliases
    matched_codes: Set[str] = set()
    for code, aliases in EXPANDED_ALIASES.items():
        for alias in aliases:
            if re.search(rf"\b{re.escape(alias)}\b", text):
                matched_codes.add(code)

    if len(matched_codes) == 1:
        code = next(iter(matched_codes))
        subj = next(s for s in CANONICAL_SUBJECTS if s["code"] == code)
        return subj, None, []
    elif len(matched_codes) > 1:
        # Filter by semester_hint if available
        if semester_hint:
            sem_matched = [
                s for s in CANONICAL_SUBJECTS if s["code"] in matched_codes and s["semester"] == semester_hint
            ]
            if len(sem_matched) == 1:
                return sem_matched[0], None, []

        candidates = [
            f"{s['code']} ({s['name']} - Sem {s['semester']})"
            for s in CANONICAL_SUBJECTS
            if s["code"] in matched_codes
        ]
        return None, "subject", candidates

    return None, None, []


def process_query(query: str) -> NLPResult:
    """
    Main entry point for the isolated IRIS Phase 8 NLP Query Processor.

    Accepts a student natural-language query string and returns a structured NLPResult.
    Performs deterministic query processing without external dependencies, ML models, or DB access.
    """
    try:
        if not query or not query.strip():
            return NLPResult(
                status=NLPStatus.NO_RESOURCE_QUERY,
                reason="Query is empty.",
            )

        # 1. Multi-request handling: Process ONLY the first request
        single_query = _split_multiple_requests(query)
        norm_text = normalize_text(single_query)

        # 2. Check for Greetings / No-Resource Query
        if norm_text in GREETING_PHRASES or any(norm_text == phrase for phrase in GREETING_PHRASES):
            return NLPResult(
                status=NLPStatus.NO_RESOURCE_QUERY,
                reason="Conversational greeting or non-academic query.",
            )

        # 3. Check for Unsupported Action Intents
        for pattern in UNSUPPORTED_PATTERNS:
            if re.search(pattern, norm_text):
                return NLPResult(
                    status=NLPStatus.UNSUPPORTED,
                    reason=f"Action intent matching '{pattern}' is outside IRIS resource retrieval scope.",
                )

        # 4. Extract Attributes
        semester = _extract_semester(norm_text)
        module = _extract_module(norm_text)
        year = _extract_year(norm_text)
        internal_exam = _extract_internal_exam(norm_text)
        category, subcategory, sub_subcategory = _extract_category_and_subcategories(norm_text)

        # 5. Resolve Subject
        subject_dict, amb_field, amb_candidates = _resolve_subject(norm_text, semester, category)

        if amb_field:
            return NLPResult(
                status=NLPStatus.AMBIGUOUS,
                category=category,
                subcategory=subcategory,
                sub_subcategory=sub_subcategory,
                semester=semester,
                module=module,
                year=year,
                internal_exam=internal_exam,
                ambiguous_field=amb_field,
                ambiguous_candidates=amb_candidates,
                reason="Multiple potential subject matches found for query terms.",
            )

        # Infer category/subcategory if subject is known and category is missing
        if subject_dict and not category:
            if "lab" in subject_dict["name"].lower() or "lab" in norm_text:
                category = "Lab Manuals"
            else:
                if module:
                    category = "Notes"

        # Check category ambiguity (e.g. unqualified "project report" or "syllabus")
        if re.search(r"\bproject\s+report\b", norm_text) and not subcategory:
            return NLPResult(
                status=NLPStatus.AMBIGUOUS,
                category="Projects",
                ambiguous_field="subcategory",
                ambiguous_candidates=["Mini Project", "Main Project"],
                reason="Project report request requires distinction between Mini Project and Main Project.",
            )

        if re.search(r"\bsyllabus\b", norm_text) and not subcategory and not sub_subcategory:
            return NLPResult(
                status=NLPStatus.AMBIGUOUS,
                category="Reference Materials",
                ambiguous_field="subcategory",
                ambiguous_candidates=["Bridge Course Syllabus", "Syllabus & Academic Guide"],
                reason="Syllabus request requires distinction between Bridge Course Syllabus and Academic Guide.",
            )

        # Check if query didn't match any academic resource intent or subject
        if not category and not subject_dict and not semester and not module:
            if any(word in norm_text for word in ["hello", "hi", "hey", "thanks", "thank", "joke", "weather"]):
                return NLPResult(
                    status=NLPStatus.NO_RESOURCE_QUERY,
                    reason="No academic resource intent detected.",
                )
            return NLPResult(
                status=NLPStatus.NO_RESOURCE_QUERY,
                reason="Query does not match any known academic resource or subject.",
            )

        subject_code = subject_dict["code"] if subject_dict else None
        subject_name = subject_dict["name"] if subject_dict else None

        # Validate year usage: Only attach year if category/subcategory supports year filtering
        valid_year = year
        if category == "Projects":
            valid_year = None  # Year is incidental metadata for Projects, not a DB retrieval parameter

        # 6. Validate Required Fields using FIELD_REQUIREMENTS_MATRIX
        missing_fields: List[str] = []

        if category == "Notes":
            if not semester:
                missing_fields.append("semester")
            if not subject_code:
                missing_fields.append("subject")
            if not module:
                missing_fields.append("module")

        elif category == "Question Papers":
            if not subcategory:
                missing_fields.append("subcategory")
            if not semester:
                missing_fields.append("semester")
            if not subject_code:
                missing_fields.append("subject")
            if subcategory == "Internal Examination":
                if not year:
                    missing_fields.append("year")
                if not internal_exam:
                    missing_fields.append("internal_exam")

        elif category == "Lab Manuals":
            if not subcategory:
                missing_fields.append("subcategory")
            if not semester:
                missing_fields.append("semester")
            if not subject_code:
                missing_fields.append("subject")
            if subcategory == "Lab Question Papers" and not year:
                missing_fields.append("year")

        elif category == "Projects":
            if not subcategory:
                missing_fields.append("subcategory")
            if not sub_subcategory:
                missing_fields.append("sub_subcategory")

        elif category == "Reference Materials":
            if not subcategory:
                missing_fields.append("subcategory")
            elif subcategory == "Bridge Course" and not sub_subcategory:
                missing_fields.append("sub_subcategory")

        elif category == "Placement Materials":
            if not subcategory:
                missing_fields.append("subcategory")

        if missing_fields:
            return NLPResult(
                status=NLPStatus.INCOMPLETE,
                category=category,
                subcategory=subcategory,
                sub_subcategory=sub_subcategory,
                semester=semester,
                subject_code=subject_code,
                subject_name=subject_name,
                module=module,
                year=valid_year,
                internal_exam=internal_exam,
                missing_fields=missing_fields,
                reason=f"Missing mandatory retrieval fields: {', '.join(missing_fields)}.",
            )

        # All validation checks passed! Return VALID result
        return NLPResult(
            status=NLPStatus.VALID,
            category=category,
            subcategory=subcategory,
            sub_subcategory=sub_subcategory,
            semester=semester,
            subject_code=subject_code,
            subject_name=subject_name,
            module=module,
            year=valid_year,
            internal_exam=internal_exam,
        )

    except Exception as err:
        logger.error(f"Error processing NLP query '{query}': {err}", exc_info=True)
        return NLPResult(
            status=NLPStatus.ERROR,
            reason="Internal error occurred while processing query.",
        )
