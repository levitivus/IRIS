"""
app/utils/keyboard.py

Utility module for constructing Telegram inline keyboards for the IRIS bot.
"""

from typing import Any, Dict, List
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from app.utils.taxonomy import CATEGORIES, TAXONOMY


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
            InlineKeyboardButton("🆕 Recently Added", callback_data="recently_added"),
            InlineKeyboardButton("📞 Contact Admin", callback_data="contact_admin"),
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
