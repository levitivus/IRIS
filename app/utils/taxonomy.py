"""
app/utils/taxonomy.py

Defines the frozen IRIS taxonomy, category rules, and automatic title generation logic.
"""

from typing import Dict, List, Optional

CATEGORIES = [
    "Question Papers",
    "Notes",
    "Lab Manuals",
    "Projects",
    "Reference Materials",
    "Placement Materials",
]

TAXONOMY = {
    "Question Papers": {
        "subcategories": ["Semester Examination", "Internal Examination", "Sample Papers"],
        "sub_subcategories": {
            "Internal Examination": ["First Internal", "Second Internal"]
        }
    },
    "Notes": {
        "subcategories": [],
        "modules": [1, 2, 3, 4, 5]
    },
    "Lab Manuals": {
        "subcategories": ["Record Samples", "Lab Question Papers", "Viva Questions", "Micro Projects"]
    },
    "Projects": {
        "subcategories": ["Mini Project", "Main Project"],
        "sub_subcategories": {
            "Mini Project": ["Abstract Template", "Title Presentation Template", "Final Presentation Template", "Project Report Template"],
            "Main Project": ["Abstract Template", "Title Presentation Template", "Final Presentation Template", "Project Report Template"],
        }
    },
    "Reference Materials": {
        "subcategories": ["Bridge Course", "Micro Project Reports", "Internship Reports", "Internship Presentations", "Syllabus & Academic Guide"],
        "sub_subcategories": {
            "Bridge Course": ["Previous Year Papers", "Sample Papers", "Syllabus"]
        }
    },
    "Placement Materials": {
        "subcategories": ["Aptitude", "Technical", "HR Interview", "Resume Templates"]
    }
}


def generate_title(
    category: str,
    subcategory: Optional[str] = None,
    sub_subcategory: Optional[str] = None,
    subject_name: Optional[str] = None,
    semester: Optional[int] = None,
    year: Optional[int] = None,
    module: Optional[int] = None,
) -> str:
    """
    Generates a standardized display title based on resource metadata.
    """
    if category == "Question Papers":
        if subcategory == "Semester Examination":
            parts = []
            if subject_name:
                parts.append(subject_name)
            if semester:
                parts.append(f"Semester {semester}")
            if year:
                parts.append(str(year))
            return " - ".join(parts) if parts else "Semester Examination Paper"
        elif subcategory == "Internal Examination":
            parts = []
            if subject_name:
                parts.append(subject_name)
            if sub_subcategory:
                parts.append(sub_subcategory)
            if semester:
                parts.append(f"Semester {semester}")
            if year:
                parts.append(str(year))
            return " - ".join(parts) if parts else "Internal Examination Paper"
        elif subcategory == "Sample Papers":
            parts = []
            if subject_name:
                parts.append(subject_name)
            parts.append("Sample Paper")
            if semester:
                parts.append(f"Semester {semester}")
            return " - ".join(parts)

    elif category == "Notes":
        parts = []
        if subject_name:
            parts.append(subject_name)
        if module:
            parts.append(f"Module {module} Notes")
        else:
            parts.append("Notes")
        return " - ".join(parts)

    elif category == "Lab Manuals":
        parts = []
        if subject_name:
            parts.append(subject_name)
        if subcategory == "Lab Question Papers":
            parts.append("Lab Question Paper")
            if semester:
                parts.append(f"Semester {semester}")
            if year:
                parts.append(str(year))
        elif subcategory == "Record Samples":
            parts.append("Record Sample")
            if semester:
                parts.append(f"Semester {semester}")
        elif subcategory == "Viva Questions":
            parts.append("Viva Questions")
            if semester:
                parts.append(f"Semester {semester}")
        elif subcategory == "Micro Projects":
            parts.append("Micro Project Sample")
            if semester:
                parts.append(f"Semester {semester}")
        else:
            if subcategory:
                parts.append(subcategory)
        return " - ".join(parts) if parts else (subcategory or "Lab Manual")

    elif category == "Projects":
        parts = []
        if subcategory:
            parts.append(subcategory)
        if sub_subcategory:
            parts.append(sub_subcategory)
        return " - ".join(parts) if parts else "Project Template"

    elif category == "Reference Materials":
        parts = []
        if subcategory:
            parts.append(subcategory)
        if sub_subcategory:
            parts.append(sub_subcategory)
        if year and sub_subcategory == "Previous Year Papers":
            parts.append(str(year))
        return " - ".join(parts) if parts else "Reference Material"

    elif category == "Placement Materials":
        return subcategory if subcategory else "Placement Material"

    # Generic Fallback
    parts = [category]
    if subcategory:
        parts.append(subcategory)
    if sub_subcategory:
        parts.append(sub_subcategory)
    return " - ".join(parts)
