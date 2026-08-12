"""
app/handlers/cgpa.py

Handler module for the IRIS CGPA / SGPA Calculator.
Implements a stateful ConversationHandler flow for calculating SGPA and credit-weighted CGPA
using the authoritative KTU MCA grading scale.
"""

from typing import Any, Dict
from telegram import Update
from telegram.ext import (
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from app.utils.cgpa import calculate_gpa, get_grade_point
from app.utils.keyboard import (
    get_cgpa_cancel_keyboard,
    get_cgpa_grades_keyboard,
    get_cgpa_menu_keyboard,
    get_cgpa_result_keyboard,
    get_main_menu_keyboard,
)

# Conversation States for CGPA Calculator
(
    STATE_CGPA_TYPE,
    STATE_CGPA_NUM_SEMESTERS,
    STATE_CGPA_NUM_SUBJECTS,
    STATE_CGPA_CREDIT,
    STATE_CGPA_GRADE,
) = range(10, 15)


def _reset_cgpa_data(context: ContextTypes.DEFAULT_TYPE) -> Dict[str, Any]:
    """Resets and initializes a fresh CGPA calculation session."""
    data = {
        "mode": "sgpa",
        "total_semesters": 1,
        "current_semester": 1,
        "subjects_per_sem": {},
        "current_subject": 1,
        "current_credit": 0.0,
        "courses": [],
    }
    context.user_data["cgpa"] = data
    return data


def _get_cgpa_data(context: ContextTypes.DEFAULT_TYPE) -> Dict[str, Any]:
    """Retrieves existing CGPA calculation session data, creating it if absent."""
    if "cgpa" not in context.user_data:
        return _reset_cgpa_data(context)
    return context.user_data["cgpa"]


async def cgpa_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Entry point for 🧮 CGPA button from main menu.
    Displays CGPA calculator options (SGPA / CGPA).
    """
    query = update.callback_query
    if query:
        await query.answer()

    _reset_cgpa_data(context)

    text = (
        "🧮 *CGPA Calculator*\n\n"
        "Calculate your SGPA or CGPA using the KTU MCA grading scale.\n\n"
        "Choose an option below:"
    )
    reply_markup = get_cgpa_menu_keyboard()

    if query and query.message:
        await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    elif update.message:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")

    return STATE_CGPA_TYPE


async def handle_cgpa_type_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Processes choice between SGPA and CGPA."""
    query = update.callback_query
    if not query or not query.data:
        return STATE_CGPA_TYPE
    await query.answer()

    selection = query.data.split(":", 1)[1]
    data = _get_cgpa_data(context)

    if selection == "sgpa":
        data["mode"] = "sgpa"
        data["total_semesters"] = 1
        data["current_semester"] = 1

        text = (
            "📊 *SGPA Calculator*\n\n"
            "Enter the number of subjects for this semester (1 to 20):"
        )
        reply_markup = get_cgpa_cancel_keyboard()
        await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
        return STATE_CGPA_NUM_SUBJECTS

    elif selection == "cgpa":
        data["mode"] = "cgpa"

        text = (
            "📈 *CGPA Calculator*\n\n"
            "Enter the number of semesters (1 to 6):"
        )
        reply_markup = get_cgpa_cancel_keyboard()
        await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
        return STATE_CGPA_NUM_SEMESTERS

    return STATE_CGPA_TYPE


async def handle_num_semesters_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Processes text input for total number of semesters."""
    if not update.message or not update.message.text:
        return STATE_CGPA_NUM_SEMESTERS

    user_text = update.message.text.strip()

    try:
        val = int(user_text)
        if not (1 <= val <= 6):
            raise ValueError("Out of range")
    except ValueError:
        await update.message.reply_text(
            "⚠️ *Invalid Input*\n\nPlease enter a valid number of semesters between 1 and 6.",
            reply_markup=get_cgpa_cancel_keyboard(),
            parse_mode="Markdown",
        )
        return STATE_CGPA_NUM_SEMESTERS

    data = _get_cgpa_data(context)
    data["total_semesters"] = val
    data["current_semester"] = 1

    text = (
        f"🗓 *Semester 1 of {val}*\n\n"
        "Enter the number of subjects for Semester 1 (1 to 20):"
    )
    reply_markup = get_cgpa_cancel_keyboard()
    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    return STATE_CGPA_NUM_SUBJECTS


async def handle_num_subjects_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Processes text input for number of subjects in current semester."""
    if not update.message or not update.message.text:
        return STATE_CGPA_NUM_SUBJECTS

    user_text = update.message.text.strip()

    try:
        val = int(user_text)
        if not (1 <= val <= 20):
            raise ValueError("Out of range")
    except ValueError:
        await update.message.reply_text(
            "⚠️ *Invalid Input*\n\nPlease enter a valid number of subjects between 1 and 20.",
            reply_markup=get_cgpa_cancel_keyboard(),
            parse_mode="Markdown",
        )
        return STATE_CGPA_NUM_SUBJECTS

    data = _get_cgpa_data(context)
    curr_sem = data.get("current_semester", 1)
    data["subjects_per_sem"][curr_sem] = val
    data["current_subject"] = 1

    total_subjs = val
    total_sems = data.get("total_semesters", 1)

    if data.get("mode") == "cgpa":
        header = f"📚 *Subject 1 of {total_subjs}* (Sem {curr_sem} of {total_sems})"
    else:
        header = f"📚 *Subject 1 of {total_subjs}*"

    text = f"{header}\n\nEnter the credit for this subject (e.g. 1 to 6):"
    reply_markup = get_cgpa_cancel_keyboard()
    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    return STATE_CGPA_CREDIT


async def handle_credit_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Processes text input for course credit."""
    if not update.message or not update.message.text:
        return STATE_CGPA_CREDIT

    user_text = update.message.text.strip()

    try:
        credit = float(user_text)
        if not (0.5 <= credit <= 10.0):
            raise ValueError("Out of range")
    except ValueError:
        await update.message.reply_text(
            "⚠️ *Invalid Input*\n\nPlease enter a valid positive credit value (e.g. 1, 2, 3, 4, 5).",
            reply_markup=get_cgpa_cancel_keyboard(),
            parse_mode="Markdown",
        )
        return STATE_CGPA_CREDIT

    data = _get_cgpa_data(context)
    data["current_credit"] = credit
    curr_subj = data.get("current_subject", 1)
    curr_sem = data.get("current_semester", 1)
    total_subjs = data.get("subjects_per_sem", {}).get(curr_sem, 1)

    text = (
        f"📚 *Subject {curr_subj} of {total_subjs}* (Credit: `{credit:g}`)\n\n"
        "Select the letter grade obtained:"
    )
    reply_markup = get_cgpa_grades_keyboard()
    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    return STATE_CGPA_GRADE


async def handle_grade_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Processes letter grade button selection, accumulates courses, and advances state or computes final GPA."""
    query = update.callback_query
    if not query or not query.data:
        return STATE_CGPA_GRADE
    await query.answer()

    grade_letter = query.data.split(":", 1)[1]
    data = _get_cgpa_data(context)
    credit = data.get("current_credit", 0.0)
    grade_point = get_grade_point(grade_letter)

    # Accumulate course record
    data["courses"].append({
        "credit": credit,
        "grade_point": grade_point,
        "grade": grade_letter,
        "semester": data.get("current_semester", 1),
    })

    curr_sem = data.get("current_semester", 1)
    total_sems = data.get("total_semesters", 1)
    subjs_in_sem = data.get("subjects_per_sem", {}).get(curr_sem, 1)
    curr_subj = data.get("current_subject", 1)

    # Advance subject index
    if curr_subj < subjs_in_sem:
        data["current_subject"] = curr_subj + 1
        next_subj = data["current_subject"]

        if data.get("mode") == "cgpa":
            header = f"📚 *Subject {next_subj} of {subjs_in_sem}* (Sem {curr_sem} of {total_sems})"
        else:
            header = f"📚 *Subject {next_subj} of {subjs_in_sem}*"

        text = f"{header}\n\nEnter the credit for this subject (e.g. 1 to 6):"
        reply_markup = get_cgpa_cancel_keyboard()
        await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
        return STATE_CGPA_CREDIT

    # If current semester subjects are finished, advance to next semester or calculate final result
    if curr_sem < total_sems:
        data["current_semester"] = curr_sem + 1
        next_sem = data["current_semester"]

        text = (
            f"🗓 *Semester {next_sem} of {total_sems}*\n\n"
            f"Enter the number of subjects for Semester {next_sem} (1 to 20):"
        )
        reply_markup = get_cgpa_cancel_keyboard()
        await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
        return STATE_CGPA_NUM_SUBJECTS

    # All subjects and semesters completed -> Calculate final Result!
    courses = data.get("courses", [])
    gpa, total_credits, total_weighted_points = calculate_gpa(courses)
    mode = data.get("mode", "sgpa")
    total_courses = len(courses)

    if mode == "cgpa":
        text = (
            "📈 *CGPA Result*\n\n"
            f"🗓 *Total Semesters:* `{total_sems}`\n"
            f"📚 *Total Courses:* `{total_courses}`\n"
            f"📖 *Total Credits:* `{total_credits:g}`\n"
            f"⭐ *Weighted Grade Points:* `{total_weighted_points:.2f}`\n\n"
            f"🏆 *CGPA:* *`{gpa:.2f}`*"
        )
    else:
        text = (
            "📊 *SGPA Result*\n\n"
            f"📚 *Total Subjects:* `{total_courses}`\n"
            f"📖 *Total Credits:* `{total_credits:g}`\n"
            f"⭐ *Weighted Grade Points:* `{total_weighted_points:.2f}`\n\n"
            f"🏆 *SGPA:* *`{gpa:.2f}`*"
        )

    reply_markup = get_cgpa_result_keyboard()
    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")

    context.user_data.pop("cgpa", None)
    return ConversationHandler.END


async def handle_cgpa_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels ongoing CGPA calculation session and returns to student main menu."""
    context.user_data.pop("cgpa", None)

    text = "🎓 Welcome to IRIS\n\nYour Academic Resource Assistant\n\nChoose an option below."
    reply_markup = get_main_menu_keyboard()

    query = update.callback_query
    if query:
        await query.answer()
        if query.message:
            await query.message.edit_text(text, reply_markup=reply_markup)
    elif update.message:
        await update.message.reply_text(text, reply_markup=reply_markup)

    return ConversationHandler.END


def get_cgpa_conversation_handler() -> ConversationHandler:
    """
    Constructs and returns the ConversationHandler for CGPA / SGPA calculation.
    """
    return ConversationHandler(
        entry_points=[
            CallbackQueryHandler(cgpa_menu_handler, pattern="^cgpa$"),
            CallbackQueryHandler(cgpa_menu_handler, pattern="^cgpa_restart$"),
        ],
        states={
            STATE_CGPA_TYPE: [
                CallbackQueryHandler(handle_cgpa_type_selection, pattern="^cgpa_type:"),
            ],
            STATE_CGPA_NUM_SEMESTERS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_num_semesters_input),
            ],
            STATE_CGPA_NUM_SUBJECTS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_num_subjects_input),
            ],
            STATE_CGPA_CREDIT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_credit_input),
            ],
            STATE_CGPA_GRADE: [
                CallbackQueryHandler(handle_grade_selection, pattern="^cgpa_grade:"),
            ],
        },
        fallbacks=[
            CallbackQueryHandler(handle_cgpa_cancel, pattern="^cgpa_cancel$"),
            CallbackQueryHandler(handle_cgpa_cancel, pattern="^student_back_to_main$"),
            CallbackQueryHandler(cgpa_menu_handler, pattern="^cgpa_restart$"),
        ],
        allow_reentry=True,
    )
