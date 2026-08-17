"""
app/utils/keyboard.py

Utility module for constructing Telegram inline keyboards for the IRIS bot (Student & Admin navigation).
"""

from typing import Any, Dict, List, Optional
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from app.utils.taxonomy import CATEGORIES, TAXONOMY

# Mapping index arrays for Phase 7 callback compression
PROJECT_SUBCATS = ["Mini Project", "Main Project"]
PROJECT_SUB_SUBCATS = [
    "Abstract Template",
    "Title Presentation Template",
    "Final Presentation Template",
    "Project Report Template",
]

LAB_SUBCATS = [
    "Record Samples",
    "Lab Question Papers",
    "Viva Questions",
    "Micro Projects",
]

PLACEMENT_SUBCATS = [
    "Aptitude",
    "Technical",
    "HR Interview",
    "Resume Templates",
]

REF_SUBCATS = [
    "Bridge Course",
    "Internship Reports",
    "Internship Presentations",
    "Syllabus & Academic Guide",
]
REF_BRIDGE_SUB_SUBCATS = [
    "Previous Year Papers",
    "Sample Papers",
    "Syllabus",
]


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """
    Builds and returns the IRIS bot Main Menu InlineKeyboardMarkup.
    """
    keyboard = [
        [
            InlineKeyboardButton("📄 Question Papers", callback_data="question_papers"),
            InlineKeyboardButton("📝 Notes", callback_data="notes"),
        ],
        [
            InlineKeyboardButton("🧪 Lab Manuals", callback_data="lab_manuals"),
            InlineKeyboardButton("💻 Projects", callback_data="projects"),
        ],
        [
            InlineKeyboardButton("📚 Reference Materials", callback_data="reference_materials"),
            InlineKeyboardButton("💼 Placement Materials", callback_data="placement_materials"),
        ],
        [
            InlineKeyboardButton("🧮 CGPA", callback_data="cgpa"),
            InlineKeyboardButton("🔍 Search", callback_data="search"),
        ],
        [
            InlineKeyboardButton("❓ Help", callback_data="help"),
            InlineKeyboardButton("📞 Contact Admin", callback_data="contact_admin"),
        ],
        [
            InlineKeyboardButton("ℹ️ About IRIS", callback_data="about_iris"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_admin_menu_keyboard() -> InlineKeyboardMarkup:
    """
    Builds and returns the IRIS Administration Panel InlineKeyboardMarkup.
    """
    keyboard = [
        [
            InlineKeyboardButton("📤 Upload Resource", callback_data="admin_upload_resource"),
            InlineKeyboardButton("📋 View Uploads", callback_data="admin_view_uploads"),
        ],
        [
            InlineKeyboardButton("📊 Statistics", callback_data="admin_statistics"),
            InlineKeyboardButton("⚙ Settings", callback_data="admin_settings"),
        ],
        [
            InlineKeyboardButton("⬅ Back to Main Menu", callback_data="admin_back_to_main"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_admin_back_keyboard() -> InlineKeyboardMarkup:
    """
    Builds a keyboard with a single ⬅ Back button to return to the Admin Panel.
    """
    keyboard = [
        [
            InlineKeyboardButton("⬅ Back", callback_data="admin_back"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


# ==============================================================================
# STUDENT QUESTION PAPER KEYBOARDS (PHASE 5)
# ==============================================================================

def get_student_qp_menu_keyboard() -> InlineKeyboardMarkup:
    """Builds subcategory menu keyboard for Student Question Papers."""
    keyboard = [
        [InlineKeyboardButton("📝 Semester Examination", callback_data="sqp_subcat:sem_exam")],
        [InlineKeyboardButton("📝 Internal Examination", callback_data="sqp_subcat:int_exam")],
        [InlineKeyboardButton("📝 Sample Papers", callback_data="sqp_subcat:sample")],
        [InlineKeyboardButton("⬅ Back to Main Menu", callback_data="student_back_to_main")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_student_qp_semesters_keyboard(subcat_code: str, semesters: List[int]) -> InlineKeyboardMarkup:
    """Builds semester selection keyboard for student Question Papers."""
    keyboard = []
    row = []
    for sem in semesters:
        row.append(InlineKeyboardButton(f"Semester {sem}", callback_data=f"sqp_sem:{subcat_code}:{sem}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    keyboard.append([
        InlineKeyboardButton("⬅ Back", callback_data="sqp_back_subcat"),
        InlineKeyboardButton("🏠 Main Menu", callback_data="student_back_to_main"),
    ])
    return InlineKeyboardMarkup(keyboard)


def get_student_qp_years_keyboard(subcat_code: str, semester: int, years: List[int]) -> InlineKeyboardMarkup:
    """Builds year selection keyboard for student Question Papers."""
    keyboard = []
    row = []
    for yr in years:
        row.append(InlineKeyboardButton(str(yr), callback_data=f"sqp_yr:{subcat_code}:{semester}:{yr}"))
        if len(row) == 3:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    keyboard.append([
        InlineKeyboardButton("⬅ Back", callback_data=f"sqp_back_sem:{subcat_code}"),
        InlineKeyboardButton("🏠 Main Menu", callback_data="student_back_to_main"),
    ])
    return InlineKeyboardMarkup(keyboard)


def get_student_qp_internals_keyboard(semester: int, year: int, internals: List[int]) -> InlineKeyboardMarkup:
    """Builds internal examination selection keyboard (First Internal / Second Internal)."""
    keyboard = []
    row = []
    for i_val in internals:
        label = "First Internal" if i_val == 1 else "Second Internal"
        row.append(InlineKeyboardButton(label, callback_data=f"sqp_int:int_exam:{semester}:{year}:{i_val}"))
    if row:
        keyboard.append(row)

    keyboard.append([
        InlineKeyboardButton("⬅ Back", callback_data=f"sqp_back_yr:int_exam:{semester}"),
        InlineKeyboardButton("🏠 Main Menu", callback_data="student_back_to_main"),
    ])
    return InlineKeyboardMarkup(keyboard)


def get_student_qp_subjects_keyboard(
    subcat_code: str,
    semester: int,
    year: int,
    internal_exam: int,
    subjects: List[Dict[str, Any]],
) -> InlineKeyboardMarkup:
    """Builds subject selection keyboard for student Question Papers."""
    keyboard = []
    for subj in subjects:
        btn_text = f"{subj['subject_code']} - {subj['subject_name']}"
        if len(btn_text) > 40:
            btn_text = f"{subj['subject_code']} - {subj['subject_name'][:30]}..."
        cb_data = f"sqp_subj:{subcat_code}:{semester}:{year}:{internal_exam}:{subj['id']}"
        keyboard.append([InlineKeyboardButton(btn_text, callback_data=cb_data)])

    if subcat_code == "sample":
        back_cb = f"sqp_back_sem:{subcat_code}"
    elif subcat_code == "int_exam":
        back_cb = f"sqp_back_int:int_exam:{semester}:{year}"
    else:
        back_cb = f"sqp_back_yr:sem_exam:{semester}"

    keyboard.append([
        InlineKeyboardButton("⬅ Back", callback_data=back_cb),
        InlineKeyboardButton("🏠 Main Menu", callback_data="student_back_to_main"),
    ])
    return InlineKeyboardMarkup(keyboard)


def get_student_qp_resource_result_keyboard(back_callback: str) -> InlineKeyboardMarkup:
    """Builds keyboard for resource result / error screens."""
    keyboard = [
        [
            InlineKeyboardButton("⬅ Back", callback_data=back_callback),
            InlineKeyboardButton("🏠 Main Menu", callback_data="student_back_to_main"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


# ==============================================================================
# STUDENT NOTES KEYBOARDS (PHASE 6)
# ==============================================================================

def get_student_notes_semesters_keyboard(semesters: List[int]) -> InlineKeyboardMarkup:
    """Builds semester selection keyboard for student Notes."""
    keyboard = []
    row = []
    for sem in semesters:
        row.append(InlineKeyboardButton(f"Semester {sem}", callback_data=f"snotes_sem:{sem}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    keyboard.append([
        InlineKeyboardButton("⬅ Back to Main Menu", callback_data="student_back_to_main"),
    ])
    return InlineKeyboardMarkup(keyboard)


def get_student_notes_subjects_keyboard(semester: int, subjects: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
    """Builds subject selection keyboard for student Notes."""
    keyboard = []
    for subj in subjects:
        btn_text = f"{subj['subject_code']} - {subj['subject_name']}"
        if len(btn_text) > 40:
            btn_text = f"{subj['subject_code']} - {subj['subject_name'][:30]}..."
        cb_data = f"snotes_subj:{semester}:{subj['id']}"
        keyboard.append([InlineKeyboardButton(btn_text, callback_data=cb_data)])

    keyboard.append([
        InlineKeyboardButton("⬅ Back", callback_data="snotes_back_sem"),
        InlineKeyboardButton("🏠 Main Menu", callback_data="student_back_to_main"),
    ])
    return InlineKeyboardMarkup(keyboard)


def get_student_notes_modules_keyboard(semester: int, subject_id: int, modules: List[int]) -> InlineKeyboardMarkup:
    """Builds module selection keyboard for student Notes."""
    keyboard = []
    row = []
    for mod in modules:
        row.append(InlineKeyboardButton(f"Module {mod}", callback_data=f"snotes_mod:{semester}:{subject_id}:{mod}"))
        if len(row) == 3:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    keyboard.append([
        InlineKeyboardButton("⬅ Back", callback_data=f"snotes_back_subj:{semester}"),
        InlineKeyboardButton("🏠 Main Menu", callback_data="student_back_to_main"),
    ])
    return InlineKeyboardMarkup(keyboard)


def get_student_notes_resource_result_keyboard(back_callback: str) -> InlineKeyboardMarkup:
    """Builds keyboard for Notes resource result / error screens."""
    keyboard = [
        [
            InlineKeyboardButton("⬅ Back", callback_data=back_callback),
            InlineKeyboardButton("🏠 Main Menu", callback_data="student_back_to_main"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


# ==============================================================================
# STUDENT PHASE 7 KEYBOARDS (PROJECTS, LAB MANUALS, PLACEMENT, REFERENCE)
# ==============================================================================

# --- PROJECTS ---

def get_student_projects_subcategories_keyboard() -> InlineKeyboardMarkup:
    """Builds subcategory menu keyboard for Projects (Mini Project, Main Project)."""
    keyboard = []
    for idx, subcat in enumerate(PROJECT_SUBCATS):
        keyboard.append([InlineKeyboardButton(subcat, callback_data=f"sproj_sub:{idx}")])
    keyboard.append([InlineKeyboardButton("⬅ Back to Main Menu", callback_data="student_back_to_main")])
    return InlineKeyboardMarkup(keyboard)


def get_student_projects_sub_subcategories_keyboard(subcat_idx: int) -> InlineKeyboardMarkup:
    """Builds template selection keyboard for Projects."""
    keyboard = []
    for idx, template in enumerate(PROJECT_SUB_SUBCATS):
        keyboard.append([InlineKeyboardButton(template, callback_data=f"sproj_item:{subcat_idx}:{idx}")])
    keyboard.append([
        InlineKeyboardButton("⬅ Back", callback_data="sproj_back_sub"),
        InlineKeyboardButton("🏠 Main Menu", callback_data="student_back_to_main"),
    ])
    return InlineKeyboardMarkup(keyboard)


# --- LAB MANUALS ---

def get_student_lab_menu_keyboard() -> InlineKeyboardMarkup:
    """Builds subcategory menu keyboard for Lab Manuals."""
    keyboard = []
    for idx, subcat in enumerate(LAB_SUBCATS):
        keyboard.append([InlineKeyboardButton(subcat, callback_data=f"slab_sub:{idx}")])
    keyboard.append([InlineKeyboardButton("⬅ Back to Main Menu", callback_data="student_back_to_main")])
    return InlineKeyboardMarkup(keyboard)


def get_student_lab_semesters_keyboard(subcat_idx: int, semesters: List[int]) -> InlineKeyboardMarkup:
    """Builds semester selection keyboard for Lab Manuals."""
    keyboard = []
    row = []
    for sem in semesters:
        row.append(InlineKeyboardButton(f"Semester {sem}", callback_data=f"slab_sem:{subcat_idx}:{sem}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    keyboard.append([
        InlineKeyboardButton("⬅ Back", callback_data="slab_back_sub"),
        InlineKeyboardButton("🏠 Main Menu", callback_data="student_back_to_main"),
    ])
    return InlineKeyboardMarkup(keyboard)


def get_student_lab_years_keyboard(subcat_idx: int, semester: int, years: List[int]) -> InlineKeyboardMarkup:
    """Builds year selection keyboard for Lab Question Papers."""
    keyboard = []
    row = []
    for yr in years:
        row.append(InlineKeyboardButton(str(yr), callback_data=f"slab_yr:{subcat_idx}:{semester}:{yr}"))
        if len(row) == 3:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    keyboard.append([
        InlineKeyboardButton("⬅ Back", callback_data=f"slab_back_sem:{subcat_idx}"),
        InlineKeyboardButton("🏠 Main Menu", callback_data="student_back_to_main"),
    ])
    return InlineKeyboardMarkup(keyboard)


def get_student_lab_subjects_keyboard(
    subcat_idx: int, semester: int, year: int, subjects: List[Dict[str, Any]]
) -> InlineKeyboardMarkup:
    """Builds subject selection keyboard for Lab Manuals."""
    keyboard = []
    for subj in subjects:
        btn_text = f"{subj['subject_code']} - {subj['subject_name']}"
        if len(btn_text) > 40:
            btn_text = f"{subj['subject_code']} - {subj['subject_name'][:30]}..."
        cb_data = f"slab_subj:{subcat_idx}:{semester}:{year}:{subj['id']}"
        keyboard.append([InlineKeyboardButton(btn_text, callback_data=cb_data)])

    back_cb = f"slab_back_yr:{subcat_idx}:{semester}" if subcat_idx == 1 else f"slab_back_sem:{subcat_idx}"
    keyboard.append([
        InlineKeyboardButton("⬅ Back", callback_data=back_cb),
        InlineKeyboardButton("🏠 Main Menu", callback_data="student_back_to_main"),
    ])
    return InlineKeyboardMarkup(keyboard)


# --- PLACEMENT MATERIALS ---

def get_student_placement_menu_keyboard() -> InlineKeyboardMarkup:
    """Builds subcategory menu keyboard for Placement Materials."""
    keyboard = []
    for idx, subcat in enumerate(PLACEMENT_SUBCATS):
        keyboard.append([InlineKeyboardButton(subcat, callback_data=f"splace_sub:{idx}")])
    keyboard.append([InlineKeyboardButton("⬅ Back to Main Menu", callback_data="student_back_to_main")])
    return InlineKeyboardMarkup(keyboard)


# --- REFERENCE MATERIALS ---

def get_student_reference_menu_keyboard() -> InlineKeyboardMarkup:
    """Builds subcategory menu keyboard for Reference Materials."""
    keyboard = []
    for idx, subcat in enumerate(REF_SUBCATS):
        keyboard.append([InlineKeyboardButton(subcat, callback_data=f"sref_sub:{idx}")])
    keyboard.append([InlineKeyboardButton("⬅ Back to Main Menu", callback_data="student_back_to_main")])
    return InlineKeyboardMarkup(keyboard)


def get_student_reference_bridge_keyboard() -> InlineKeyboardMarkup:
    """Builds sub-subcategory selection keyboard for Bridge Course."""
    keyboard = []
    for idx, subsub in enumerate(REF_BRIDGE_SUB_SUBCATS):
        keyboard.append([InlineKeyboardButton(subsub, callback_data=f"sref_subsub:0:{idx}")])
    keyboard.append([
        InlineKeyboardButton("⬅ Back", callback_data="sref_back_sub"),
        InlineKeyboardButton("🏠 Main Menu", callback_data="student_back_to_main"),
    ])
    return InlineKeyboardMarkup(keyboard)


def get_student_reference_years_keyboard(subsub_idx: int, years: List[int]) -> InlineKeyboardMarkup:
    """Builds year selection keyboard for Bridge Course -> Previous Year Papers."""
    keyboard = []
    row = []
    for yr in years:
        row.append(InlineKeyboardButton(str(yr), callback_data=f"sref_yr:0:{subsub_idx}:{yr}"))
        if len(row) == 3:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    keyboard.append([
        InlineKeyboardButton("⬅ Back", callback_data="sref_back_subsub:0"),
        InlineKeyboardButton("🏠 Main Menu", callback_data="student_back_to_main"),
    ])
    return InlineKeyboardMarkup(keyboard)


def get_student_phase7_resource_result_keyboard(back_callback: str) -> InlineKeyboardMarkup:
    """Generic keyboard for Phase 7 resource result / error screens."""
    keyboard = [
        [
            InlineKeyboardButton("⬅ Back", callback_data=back_callback),
            InlineKeyboardButton("🏠 Main Menu", callback_data="student_back_to_main"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


# ==============================================================================
# UPLOAD WIZARD KEYBOARDS
# ==============================================================================

def get_upload_categories_keyboard() -> InlineKeyboardMarkup:
    """Builds category selection keyboard for upload wizard."""
    keyboard = []
    for cat in CATEGORIES:
        keyboard.append([InlineKeyboardButton(cat, callback_data=f"up_cat:{cat}")])
    keyboard.append([
        InlineKeyboardButton("❌ Cancel", callback_data="upload_cancel")
    ])
    return InlineKeyboardMarkup(keyboard)


def get_upload_subcategories_keyboard(category: str) -> InlineKeyboardMarkup:
    """Builds subcategory selection keyboard for upload wizard."""
    keyboard = []
    subcats = TAXONOMY.get(category, {}).get("subcategories", [])
    for sub in subcats:
        keyboard.append([InlineKeyboardButton(sub, callback_data=f"up_subcat:{sub}")])
    keyboard.append([
        InlineKeyboardButton("⬅ Back", callback_data="upload_back"),
        InlineKeyboardButton("❌ Cancel", callback_data="upload_cancel")
    ])
    return InlineKeyboardMarkup(keyboard)


def get_upload_sub_subcategories_keyboard(category: str, subcategory: str) -> InlineKeyboardMarkup:
    """Builds sub-subcategory selection keyboard for upload wizard."""
    keyboard = []
    sub_subcats = TAXONOMY.get(category, {}).get("sub_subcategories", {}).get(subcategory, [])
    for subsub in sub_subcats:
        keyboard.append([InlineKeyboardButton(subsub, callback_data=f"up_subsubcat:{subsub}")])
    keyboard.append([
        InlineKeyboardButton("⬅ Back", callback_data="upload_back"),
        InlineKeyboardButton("❌ Cancel", callback_data="upload_cancel")
    ])
    return InlineKeyboardMarkup(keyboard)


def get_upload_semesters_keyboard() -> InlineKeyboardMarkup:
    """Builds semester selection keyboard (Semesters 1-4)."""
    keyboard = [
        [
            InlineKeyboardButton("Semester 1", callback_data="up_sem:1"),
            InlineKeyboardButton("Semester 2", callback_data="up_sem:2"),
        ],
        [
            InlineKeyboardButton("Semester 3", callback_data="up_sem:3"),
            InlineKeyboardButton("Semester 4", callback_data="up_sem:4"),
        ],
        [
            InlineKeyboardButton("⬅ Back", callback_data="upload_back"),
            InlineKeyboardButton("❌ Cancel", callback_data="upload_cancel")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_upload_years_keyboard(start_year: int = 2020, end_year: int = 2026) -> InlineKeyboardMarkup:
    """Builds year selection keyboard."""
    keyboard = []
    row = []
    for yr in range(start_year, end_year + 1):
        row.append(InlineKeyboardButton(str(yr), callback_data=f"up_year:{yr}"))
        if len(row) == 3:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    keyboard.append([
        InlineKeyboardButton("⬅ Back", callback_data="upload_back"),
        InlineKeyboardButton("❌ Cancel", callback_data="upload_cancel")
    ])
    return InlineKeyboardMarkup(keyboard)


def get_upload_internals_keyboard() -> InlineKeyboardMarkup:
    """Builds internal exam selection keyboard."""
    keyboard = [
        [
            InlineKeyboardButton("First Internal", callback_data="up_internal:First Internal"),
            InlineKeyboardButton("Second Internal", callback_data="up_internal:Second Internal"),
        ],
        [
            InlineKeyboardButton("⬅ Back", callback_data="upload_back"),
            InlineKeyboardButton("❌ Cancel", callback_data="upload_cancel")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_upload_modules_keyboard() -> InlineKeyboardMarkup:
    """Builds module selection keyboard (Modules 1-5)."""
    keyboard = [
        [
            InlineKeyboardButton("Module 1", callback_data="up_module:1"),
            InlineKeyboardButton("Module 2", callback_data="up_module:2"),
            InlineKeyboardButton("Module 3", callback_data="up_module:3"),
        ],
        [
            InlineKeyboardButton("Module 4", callback_data="up_module:4"),
            InlineKeyboardButton("Module 5", callback_data="up_module:5"),
        ],
        [
            InlineKeyboardButton("⬅ Back", callback_data="upload_back"),
            InlineKeyboardButton("❌ Cancel", callback_data="upload_cancel")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_upload_subjects_keyboard(subjects: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
    """Builds subject selection keyboard."""
    keyboard = []
    for subj in subjects:
        btn_text = f"{subj['subject_code']} - {subj['subject_name']}"
        if len(btn_text) > 40:
            btn_text = f"{subj['subject_code']} - {subj['subject_name'][:30]}..."
        keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"up_subj:{subj['id']}")])
    keyboard.append([
        InlineKeyboardButton("⬅ Back", callback_data="upload_back"),
        InlineKeyboardButton("❌ Cancel", callback_data="upload_cancel")
    ])
    return InlineKeyboardMarkup(keyboard)


def get_upload_document_prompt_keyboard() -> InlineKeyboardMarkup:
    """Builds keyboard displayed when prompting for document upload."""
    keyboard = [
        [
            InlineKeyboardButton("⬅ Back", callback_data="upload_back"),
            InlineKeyboardButton("❌ Cancel", callback_data="upload_cancel")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_contact_admin_keyboard() -> InlineKeyboardMarkup:
    """Builds keyboard for Contact Admin screen with Telegram link and Back / Main Menu navigation."""
    keyboard = [
        [
            InlineKeyboardButton("💬 Contact Admin", url="https://t.me/raspu1in"),
        ],
        [
            InlineKeyboardButton("⬅ Back", callback_data="student_back_to_main"),
            InlineKeyboardButton("🏠 Main Menu", callback_data="student_back_to_main"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


# ==============================================================================
# CGPA CALCULATOR KEYBOARDS
# ==============================================================================

def get_cgpa_menu_keyboard() -> InlineKeyboardMarkup:
    """Builds initial menu keyboard for CGPA Calculator."""
    keyboard = [
        [
            InlineKeyboardButton("📊 Calculate SGPA", callback_data="cgpa_type:sgpa"),
            InlineKeyboardButton("📈 Calculate CGPA", callback_data="cgpa_type:cgpa"),
        ],
        [
            InlineKeyboardButton("⬅ Back to Main Menu", callback_data="student_back_to_main"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_cgpa_cancel_keyboard() -> InlineKeyboardMarkup:
    """Builds keyboard with a single Cancel button."""
    keyboard = [
        [
            InlineKeyboardButton("❌ Cancel", callback_data="cgpa_cancel"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_cgpa_grades_keyboard() -> InlineKeyboardMarkup:
    """Builds letter grade selection keyboard for KTU MCA scale."""
    keyboard = [
        [
            InlineKeyboardButton("S (10)", callback_data="cgpa_grade:S"),
            InlineKeyboardButton("A+ (9)", callback_data="cgpa_grade:A+"),
            InlineKeyboardButton("A (8.5)", callback_data="cgpa_grade:A"),
        ],
        [
            InlineKeyboardButton("B+ (8)", callback_data="cgpa_grade:B+"),
            InlineKeyboardButton("B (7)", callback_data="cgpa_grade:B"),
            InlineKeyboardButton("C+ (6)", callback_data="cgpa_grade:C+"),
        ],
        [
            InlineKeyboardButton("C (5)", callback_data="cgpa_grade:C"),
            InlineKeyboardButton("F (0)", callback_data="cgpa_grade:F"),
            InlineKeyboardButton("FE (0)", callback_data="cgpa_grade:FE"),
            InlineKeyboardButton("Ab (0)", callback_data="cgpa_grade:Ab"),
        ],
        [
            InlineKeyboardButton("❌ Cancel", callback_data="cgpa_cancel"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_cgpa_result_keyboard() -> InlineKeyboardMarkup:
    """Builds result screen keyboard for CGPA Calculator."""
    keyboard = [
        [
            InlineKeyboardButton("🔄 Calculate Again", callback_data="cgpa_restart"),
            InlineKeyboardButton("🏠 Main Menu", callback_data="student_back_to_main"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_help_keyboard() -> InlineKeyboardMarkup:
    """Builds keyboard for Help screen with Back / Main Menu navigation."""
    keyboard = [
        [
            InlineKeyboardButton("⬅ Back", callback_data="student_back_to_main"),
            InlineKeyboardButton("🏠 Main Menu", callback_data="student_back_to_main"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_about_keyboard() -> InlineKeyboardMarkup:
    """Builds keyboard for About screen with developer link and Back / Main Menu navigation."""
    keyboard = [
        [
            InlineKeyboardButton("💬 Contact Developer", url="https://t.me/raspu1in"),
        ],
        [
            InlineKeyboardButton("⬅ Back", callback_data="student_back_to_main"),
            InlineKeyboardButton("🏠 Main Menu", callback_data="student_back_to_main"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_search_prompt_keyboard() -> InlineKeyboardMarkup:
    """Builds keyboard for Search prompt screen with Main Menu navigation."""
    keyboard = [
        [
            InlineKeyboardButton("🏠 Main Menu", callback_data="student_back_to_main"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_search_result_keyboard() -> InlineKeyboardMarkup:
    """Builds keyboard for Search diagnostic result screen with Search Again and Main Menu navigation."""
    keyboard = [
        [
            InlineKeyboardButton("🔍 Search Again", callback_data="search"),
            InlineKeyboardButton("🏠 Main Menu", callback_data="student_back_to_main"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)





