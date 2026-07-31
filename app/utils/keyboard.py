"""
app/utils/keyboard.py

Utility module for constructing Telegram inline keyboards for the IRIS bot.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


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
