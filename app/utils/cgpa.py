"""
app/utils/cgpa.py

Centralized KTU MCA grading configuration and SGPA / CGPA calculation utilities.
"""

from typing import Dict, List, Tuple

# Authoritative KTU MCA Letter Grade to Grade Point Mapping
GRADE_POINTS: Dict[str, float] = {
    "S": 10.0,
    "A+": 9.0,
    "A": 8.5,
    "B+": 8.0,
    "B": 7.0,
    "C+": 6.0,
    "C": 5.0,
    "F": 0.0,
    "FE": 0.0,
    "Ab": 0.0,
}


def get_grade_point(letter_grade: str) -> float:
    """
    Returns the grade point for a given letter grade according to the KTU MCA scale.
    Returns 0.0 for invalid/unknown grades.
    """
    return GRADE_POINTS.get(letter_grade.strip(), 0.0)


def calculate_gpa(courses: List[Dict[str, float]]) -> Tuple[float, float, float]:
    """
    Calculates weighted GPA (SGPA or CGPA) from a list of courses.
    Each course entry must contain: 'credit' (float) and 'grade_point' (float).

    Returns:
        Tuple[float, float, float]: (gpa, total_credits, total_weighted_points)
    """
    if not courses:
        return 0.0, 0.0, 0.0

    total_credits = sum(c.get("credit", 0.0) for c in courses)
    total_weighted_points = sum(c.get("credit", 0.0) * c.get("grade_point", 0.0) for c in courses)

    if total_credits <= 0:
        return 0.0, 0.0, total_weighted_points

    gpa = total_weighted_points / total_credits
    return gpa, total_credits, total_weighted_points
