"""
app/handlers/student_retrieval.py

Handler module for student academic resource retrieval:
- Phase 5: Question Papers
- Phase 6: Student Notes
- Phase 7: Projects, Lab Manuals, Placement Materials, Reference Materials
Implements deterministic button-driven navigation and document delivery via Telegram repository file IDs.
"""

from typing import Optional
from telegram import Update
from telegram.ext import ContextTypes

from app.services.resource_service import (
    get_lab_manuals_available_semesters,
    get_lab_manuals_available_subjects,
    get_lab_manuals_available_years,
    get_lab_manuals_resources,
    get_notes_available_modules,
    get_notes_available_semesters,
    get_notes_available_subjects,
    get_notes_resources,
    get_placement_resources,
    get_projects_resources,
    get_qp_available_internals,
    get_qp_available_semesters,
    get_qp_available_subjects,
    get_qp_available_years,
    get_qp_resources,
    get_reference_available_years,
    get_reference_resources,
    get_subject_by_id,
)
from app.utils.keyboard import (
    LAB_SUBCATS,
    PLACEMENT_SUBCATS,
    PROJECT_SUB_SUBCATS,
    PROJECT_SUBCATS,
    REF_BRIDGE_SUB_SUBCATS,
    REF_SUBCATS,
    get_main_menu_keyboard,
    get_student_lab_menu_keyboard,
    get_student_lab_semesters_keyboard,
    get_student_lab_subjects_keyboard,
    get_student_lab_years_keyboard,
    get_student_notes_modules_keyboard,
    get_student_notes_resource_result_keyboard,
    get_student_notes_semesters_keyboard,
    get_student_notes_subjects_keyboard,
    get_student_phase7_resource_result_keyboard,
    get_student_placement_menu_keyboard,
    get_student_projects_sub_subcategories_keyboard,
    get_student_projects_subcategories_keyboard,
    get_student_qp_internals_keyboard,
    get_student_qp_menu_keyboard,
    get_student_qp_resource_result_keyboard,
    get_student_qp_semesters_keyboard,
    get_student_qp_subjects_keyboard,
    get_student_qp_years_keyboard,
    get_student_reference_bridge_keyboard,
    get_student_reference_menu_keyboard,
    get_student_reference_years_keyboard,
)

# Mapping from subcategory code to full subcategory string for Question Papers
SUBCAT_MAP = {
    "sem_exam": "Semester Examination",
    "int_exam": "Internal Examination",
    "sample": "Sample Papers",
}


# Helper function to deliver PDF document safely via telegram_file_id
async def _deliver_student_document(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    resources: list,
    back_callback: str,
    category_name: str,
) -> None:
    query = update.callback_query
    if not query or not query.message:
        return

    if not resources:
        text = (
            f"📄 *Resource Not Available*\n\n"
            f"No {category_name.lower()} resources were found for the selected combination.\n\n"
            "Please try another option."
        )
        reply_markup = get_student_phase7_resource_result_keyboard(back_callback)
        await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
        return

    resource = resources[0]
    file_id = resource.get("telegram_file_id")

    if not file_id:
        print(f"Error: {category_name} Resource ID {resource['id']} ('{resource['title']}') exists but telegram_file_id is missing.")
        text = (
            "⚠️ *Resource Error*\n\n"
            "The resource exists in the database, but its stored Telegram file reference is unavailable.\n\n"
            "Please contact the administrator."
        )
        reply_markup = get_student_phase7_resource_result_keyboard(back_callback)
        await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
        return

    try:
        caption = f"📄 {resource['title']}"
        await context.bot.send_document(
            chat_id=query.message.chat_id,
            document=file_id,
            caption=caption
        )
        text = f"✅ *{category_name} Delivered!*\n\n📌 *{resource['title']}*"
        reply_markup = get_student_phase7_resource_result_keyboard(back_callback)
        await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    except Exception as error:
        print(f"Error sending Telegram document {file_id}: {error}")
        text = (
            "⚠️ *Delivery Error*\n\n"
            "Failed to send document from Telegram repository. Please try again later."
        )
        reply_markup = get_student_phase7_resource_result_keyboard(back_callback)
        await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")


# ==============================================================================
# STUDENT QUESTION PAPER RETRIEVAL HANDLERS (PHASE 5)
# ==============================================================================

async def student_qp_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query:
        return
    await query.answer()

    text = "📄 *Question Papers*\n\nChoose examination type:"
    reply_markup = get_student_qp_menu_keyboard()
    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def student_qp_subcat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.data:
        return
    await query.answer()

    subcat_code = query.data.split(":", 1)[1]
    subcategory = SUBCAT_MAP.get(subcat_code, "Semester Examination")
    semesters = get_qp_available_semesters(subcategory)

    if not semesters:
        text = f"📄 *Resource Not Available*\n\nNo question papers are available for *{subcategory}* yet.\n\nPlease try another option."
        reply_markup = get_student_qp_menu_keyboard()
        await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
        return

    text = f"📄 *Question Papers → {subcategory}*\n\nChoose Semester:"
    reply_markup = get_student_qp_semesters_keyboard(subcat_code, semesters)
    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def student_qp_sem_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.data:
        return
    await query.answer()

    parts = query.data.split(":")
    subcat_code = parts[1]
    semester = int(parts[2])
    subcategory = SUBCAT_MAP.get(subcat_code, "Semester Examination")

    if subcat_code in ["sem_exam", "int_exam"]:
        years = get_qp_available_years(subcategory, semester)
        if not years:
            text = (
                f"📄 *Resource Not Available*\n\n"
                f"No question papers are available for *{subcategory}* (Semester {semester}) yet.\n\n"
                "Please try another option."
            )
            reply_markup = get_student_qp_semesters_keyboard(
                subcat_code, get_qp_available_semesters(subcategory)
            )
            await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
            return

        text = f"🗓 *Question Papers → {subcategory} (Semester {semester})*\n\nChoose Year:"
        reply_markup = get_student_qp_years_keyboard(subcat_code, semester, years)
        await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        subjects = get_qp_available_subjects(subcategory, semester)
        if not subjects:
            text = (
                f"📄 *Resource Not Available*\n\n"
                f"No sample papers are available for *Semester {semester}* yet.\n\n"
                "Please try another option."
            )
            reply_markup = get_student_qp_semesters_keyboard(
                subcat_code, get_qp_available_semesters(subcategory)
            )
            await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
            return

        text = f"📚 *Question Papers → Sample Papers (Semester {semester})*\n\nChoose Subject:"
        reply_markup = get_student_qp_subjects_keyboard(
            subcat_code, semester, 0, 0, subjects
        )
        await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def student_qp_year_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.data:
        return
    await query.answer()

    parts = query.data.split(":")
    subcat_code = parts[1]
    semester = int(parts[2])
    year = int(parts[3])
    subcategory = SUBCAT_MAP.get(subcat_code, "Semester Examination")

    if subcat_code == "int_exam":
        internals = get_qp_available_internals(semester, year)
        if not internals:
            text = (
                f"📄 *Resource Not Available*\n\n"
                f"No internal examination papers are available for *Semester {semester}, {year}* yet.\n\n"
                "Please try another option."
            )
            reply_markup = get_student_qp_years_keyboard(
                subcat_code, semester, get_qp_available_years(subcategory, semester)
            )
            await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
            return

        text = f"📝 *Internal Examination (Sem {semester}, {year})*\n\nChoose Examination:"
        reply_markup = get_student_qp_internals_keyboard(semester, year, internals)
        await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        subjects = get_qp_available_subjects(subcategory, semester, year=year)
        if not subjects:
            text = (
                f"📄 *Resource Not Available*\n\n"
                f"No examination papers are available for *Semester {semester}, {year}* yet.\n\n"
                "Please try another option."
            )
            reply_markup = get_student_qp_years_keyboard(
                subcat_code, semester, get_qp_available_years(subcategory, semester)
            )
            await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
            return

        text = f"📚 *Semester Examination (Sem {semester}, {year})*\n\nChoose Subject:"
        reply_markup = get_student_qp_subjects_keyboard(
            subcat_code, semester, year, 0, subjects
        )
        await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def student_qp_internal_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.data:
        return
    await query.answer()

    parts = query.data.split(":")
    subcat_code = parts[1]
    semester = int(parts[2])
    year = int(parts[3])
    internal_exam = int(parts[4])
    subcategory = SUBCAT_MAP.get(subcat_code, "Internal Examination")

    subjects = get_qp_available_subjects(
        subcategory, semester, year=year, internal_exam=internal_exam
    )
    internal_label = "First Internal" if internal_exam == 1 else "Second Internal"

    if not subjects:
        text = (
            f"📄 *Resource Not Available*\n\n"
            f"No papers are available for *{internal_label} (Sem {semester}, {year})* yet.\n\n"
            "Please try another option."
        )
        reply_markup = get_student_qp_internals_keyboard(
            semester, year, get_qp_available_internals(semester, year)
        )
        await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
        return

    text = f"📚 *{internal_label} (Sem {semester}, {year})*\n\nChoose Subject:"
    reply_markup = get_student_qp_subjects_keyboard(
        subcat_code, semester, year, internal_exam, subjects
    )
    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def student_qp_subject_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.data or not query.message:
        return
    await query.answer()

    parts = query.data.split(":")
    subcat_code = parts[1]
    semester = int(parts[2])
    year = int(parts[3]) if parts[3] != "0" else None
    internal_exam = int(parts[4]) if parts[4] != "0" else None
    subject_id = int(parts[5])

    subcategory = SUBCAT_MAP.get(subcat_code, "Semester Examination")

    if subcat_code == "sample":
        back_cb = f"sqp_sem:{subcat_code}:{semester}"
    elif subcat_code == "int_exam":
        back_cb = f"sqp_int:int_exam:{semester}:{year}:{internal_exam}"
    else:
        back_cb = f"sqp_yr:sem_exam:{semester}:{year}"

    resources = get_qp_resources(
        subcategory, semester, subject_id, year=year, internal_exam=internal_exam
    )
    await _deliver_student_document(update, context, resources, back_cb, "Question Paper")


async def student_qp_back_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.data:
        return
    await query.answer()

    data = query.data
    if data == "sqp_back_subcat":
        text = "📄 *Question Papers*\n\nChoose examination type:"
        reply_markup = get_student_qp_menu_keyboard()
        await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")

    elif data.startswith("sqp_back_sem:"):
        subcat_code = data.split(":")[1]
        subcategory = SUBCAT_MAP.get(subcat_code, "Semester Examination")
        semesters = get_qp_available_semesters(subcategory)
        text = f"📄 *Question Papers → {subcategory}*\n\nChoose Semester:"
        reply_markup = get_student_qp_semesters_keyboard(subcat_code, semesters)
        await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")

    elif data.startswith("sqp_back_yr:"):
        parts = data.split(":")
        subcat_code = parts[1]
        semester = int(parts[2])
        subcategory = SUBCAT_MAP.get(subcat_code, "Semester Examination")
        years = get_qp_available_years(subcategory, semester)
        text = f"🗓 *Question Papers → {subcategory} (Semester {semester})*\n\nChoose Year:"
        reply_markup = get_student_qp_years_keyboard(subcat_code, semester, years)
        await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")

    elif data.startswith("sqp_back_int:"):
        parts = data.split(":")
        subcat_code = parts[1]
        semester = int(parts[2])
        year = int(parts[3])
        internals = get_qp_available_internals(semester, year)
        text = f"📝 *Internal Examination (Sem {semester}, {year})*\n\nChoose Examination:"
        reply_markup = get_student_qp_internals_keyboard(semester, year, internals)
        await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")


# ==============================================================================
# STUDENT NOTES RETRIEVAL HANDLERS (PHASE 6)
# ==============================================================================

async def student_notes_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query:
        return
    await query.answer()

    semesters = get_notes_available_semesters()
    if not semesters:
        text = "📝 *Resource Not Available*\n\nNo notes are available yet."
        reply_markup = get_main_menu_keyboard()
        await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
        return

    text = "📝 *Notes*\n\nChoose Semester:"
    reply_markup = get_student_notes_semesters_keyboard(semesters)
    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def student_notes_sem_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.data:
        return
    await query.answer()

    semester = int(query.data.split(":", 1)[1])
    subjects = get_notes_available_subjects(semester)

    if not subjects:
        text = f"📝 *Resource Not Available*\n\nNo notes are available for *Semester {semester}* yet.\n\nPlease try another option."
        reply_markup = get_student_notes_semesters_keyboard(get_notes_available_semesters())
        await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
        return

    text = f"📚 *Notes (Semester {semester})*\n\nChoose Subject:"
    reply_markup = get_student_notes_subjects_keyboard(semester, subjects)
    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def student_notes_subj_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.data:
        return
    await query.answer()

    parts = query.data.split(":")
    semester = int(parts[1])
    subject_id = int(parts[2])

    modules = get_notes_available_modules(semester, subject_id)
    subject = get_subject_by_id(subject_id)
    subject_name = subject["subject_name"] if subject else "Subject"

    if not modules:
        text = f"📝 *Resource Not Available*\n\nNo notes are available for *{subject_name} (Semester {semester})* yet.\n\nPlease try another option."
        reply_markup = get_student_notes_subjects_keyboard(semester, get_notes_available_subjects(semester))
        await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
        return

    text = f"📝 *Notes → {subject_name} (Sem {semester})*\n\nChoose Module:"
    reply_markup = get_student_notes_modules_keyboard(semester, subject_id, modules)
    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def student_notes_mod_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.data or not query.message:
        return
    await query.answer()

    parts = query.data.split(":")
    semester = int(parts[1])
    subject_id = int(parts[2])
    module = int(parts[3])

    subj_back_cb = f"snotes_subj:{semester}:{subject_id}"
    resources = get_notes_resources(semester, subject_id, module)
    await _deliver_student_document(update, context, resources, subj_back_cb, "Notes")


async def student_notes_back_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.data:
        return
    await query.answer()

    data = query.data
    if data == "snotes_back_sem":
        semesters = get_notes_available_semesters()
        text = "📝 *Notes*\n\nChoose Semester:"
        reply_markup = get_student_notes_semesters_keyboard(semesters)
        await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")

    elif data.startswith("snotes_back_subj:"):
        semester = int(data.split(":")[1])
        subjects = get_notes_available_subjects(semester)
        text = f"📚 *Notes (Semester {semester})*\n\nChoose Subject:"
        reply_markup = get_student_notes_subjects_keyboard(semester, subjects)
        await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")


# ==============================================================================
# STUDENT PHASE 7 HANDLERS (PROJECTS, LAB MANUALS, PLACEMENT, REFERENCE)
# ==============================================================================

# --- 1. PROJECTS HANDLERS ---

async def student_projects_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Entry handler for 💻 Projects button."""
    query = update.callback_query
    if not query:
        return
    await query.answer()

    text = "💻 *Projects*\n\nSelect project type:"
    reply_markup = get_student_projects_subcategories_keyboard()
    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def student_projects_subcat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Processes subcategory selection (Mini Project, Main Project)."""
    query = update.callback_query
    if not query or not query.data:
        return
    await query.answer()

    subcat_idx = int(query.data.split(":", 1)[1])
    subcategory = PROJECT_SUBCATS[subcat_idx]

    text = f"💻 *Projects → {subcategory}*\n\nSelect template type:"
    reply_markup = get_student_projects_sub_subcategories_keyboard(subcat_idx)
    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def student_projects_item_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Processes template item selection for Projects."""
    query = update.callback_query
    if not query or not query.data:
        return
    await query.answer()

    parts = query.data.split(":")
    subcat_idx = int(parts[1])
    subsub_idx = int(parts[2])

    subcategory = PROJECT_SUBCATS[subcat_idx]
    sub_subcategory = PROJECT_SUB_SUBCATS[subsub_idx]

    back_cb = f"sproj_sub:{subcat_idx}"
    resources = get_projects_resources(subcategory, sub_subcategory)
    await _deliver_student_document(update, context, resources, back_cb, "Project Template")


async def student_projects_back_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles Back navigation for Projects."""
    query = update.callback_query
    if not query:
        return
    await query.answer()

    text = "💻 *Projects*\n\nSelect project type:"
    reply_markup = get_student_projects_subcategories_keyboard()
    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")


# --- 2. LAB MANUALS HANDLERS ---

async def student_lab_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Entry handler for 🧪 Lab Manuals button."""
    query = update.callback_query
    if not query:
        return
    await query.answer()

    text = "🧪 *Lab Manuals*\n\nChoose subcategory:"
    reply_markup = get_student_lab_menu_keyboard()
    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def student_lab_subcat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Processes Lab Manuals subcategory selection."""
    query = update.callback_query
    if not query or not query.data:
        return
    await query.answer()

    subcat_idx = int(query.data.split(":", 1)[1])
    subcategory = LAB_SUBCATS[subcat_idx]

    semesters = get_lab_manuals_available_semesters(subcategory)
    if not semesters:
        text = f"🧪 *Resource Not Available*\n\nNo lab manuals are available for *{subcategory}* yet."
        reply_markup = get_student_lab_menu_keyboard()
        await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
        return

    text = f"🧪 *Lab Manuals → {subcategory}*\n\nChoose Semester:"
    reply_markup = get_student_lab_semesters_keyboard(subcat_idx, semesters)
    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def student_lab_sem_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Processes semester selection for Lab Manuals."""
    query = update.callback_query
    if not query or not query.data:
        return
    await query.answer()

    parts = query.data.split(":")
    subcat_idx = int(parts[1])
    semester = int(parts[2])
    subcategory = LAB_SUBCATS[subcat_idx]

    if subcat_idx == 1:  # Lab Question Papers
        years = get_lab_manuals_available_years(subcategory, semester)
        if not years:
            text = f"🧪 *Resource Not Available*\n\nNo lab question papers available for *Semester {semester}*."
            reply_markup = get_student_lab_semesters_keyboard(
                subcat_idx, get_lab_manuals_available_semesters(subcategory)
            )
            await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
            return

        text = f"🗓 *Lab Question Papers (Semester {semester})*\n\nChoose Year:"
        reply_markup = get_student_lab_years_keyboard(subcat_idx, semester, years)
        await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        subjects = get_lab_manuals_available_subjects(subcategory, semester)
        if not subjects:
            text = f"🧪 *Resource Not Available*\n\nNo {subcategory.lower()} available for *Semester {semester}*."
            reply_markup = get_student_lab_semesters_keyboard(
                subcat_idx, get_lab_manuals_available_semesters(subcategory)
            )
            await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
            return

        text = f"📚 *{subcategory} (Semester {semester})*\n\nChoose Subject:"
        reply_markup = get_student_lab_subjects_keyboard(subcat_idx, semester, 0, subjects)
        await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def student_lab_yr_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Processes year selection for Lab Question Papers."""
    query = update.callback_query
    if not query or not query.data:
        return
    await query.answer()

    parts = query.data.split(":")
    subcat_idx = int(parts[1])
    semester = int(parts[2])
    year = int(parts[3])
    subcategory = LAB_SUBCATS[subcat_idx]

    subjects = get_lab_manuals_available_subjects(subcategory, semester, year=year)
    if not subjects:
        text = f"🧪 *Resource Not Available*\n\nNo lab question papers available for *Sem {semester}, {year}*."
        reply_markup = get_student_lab_years_keyboard(
            subcat_idx, semester, get_lab_manuals_available_years(subcategory, semester)
        )
        await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
        return

    text = f"📚 *Lab Question Papers (Sem {semester}, {year})*\n\nChoose Subject:"
    reply_markup = get_student_lab_subjects_keyboard(subcat_idx, semester, year, subjects)
    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def student_lab_subj_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Processes subject selection and delivers Lab Manual document."""
    query = update.callback_query
    if not query or not query.data:
        return
    await query.answer()

    parts = query.data.split(":")
    subcat_idx = int(parts[1])
    semester = int(parts[2])
    year = int(parts[3]) if parts[3] != "0" else None
    subject_id = int(parts[4])
    subcategory = LAB_SUBCATS[subcat_idx]

    back_cb = f"slab_yr:{subcat_idx}:{semester}:{year}" if year else f"slab_sem:{subcat_idx}:{semester}"
    resources = get_lab_manuals_resources(subcategory, semester, subject_id, year=year)
    await _deliver_student_document(update, context, resources, back_cb, "Lab Manual")


async def student_lab_back_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles Back navigation for Lab Manuals."""
    query = update.callback_query
    if not query or not query.data:
        return
    await query.answer()

    data = query.data
    if data == "slab_back_sub":
        text = "🧪 *Lab Manuals*\n\nChoose subcategory:"
        reply_markup = get_student_lab_menu_keyboard()
        await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")

    elif data.startswith("slab_back_sem:"):
        subcat_idx = int(data.split(":")[1])
        subcategory = LAB_SUBCATS[subcat_idx]
        semesters = get_lab_manuals_available_semesters(subcategory)
        text = f"🧪 *Lab Manuals → {subcategory}*\n\nChoose Semester:"
        reply_markup = get_student_lab_semesters_keyboard(subcat_idx, semesters)
        await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")

    elif data.startswith("slab_back_yr:"):
        parts = data.split(":")
        subcat_idx = int(parts[1])
        semester = int(parts[2])
        subcategory = LAB_SUBCATS[subcat_idx]
        years = get_lab_manuals_available_years(subcategory, semester)
        text = f"🗓 *Lab Question Papers (Semester {semester})*\n\nChoose Year:"
        reply_markup = get_student_lab_years_keyboard(subcat_idx, semester, years)
        await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")


# --- 3. PLACEMENT MATERIALS HANDLERS ---

async def student_placement_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Entry handler for 💼 Placement Materials button."""
    query = update.callback_query
    if not query:
        return
    await query.answer()

    text = "💼 *Placement Materials*\n\nChoose category:"
    reply_markup = get_student_placement_menu_keyboard()
    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def student_placement_subcat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Processes subcategory selection and delivers Placement Material document."""
    query = update.callback_query
    if not query or not query.data:
        return
    await query.answer()

    subcat_idx = int(query.data.split(":", 1)[1])
    subcategory = PLACEMENT_SUBCATS[subcat_idx]

    back_cb = "student_back_to_main"
    resources = get_placement_resources(subcategory)
    await _deliver_student_document(update, context, resources, back_cb, "Placement Material")


# --- 4. REFERENCE MATERIALS HANDLERS ---

async def student_reference_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Entry handler for 📚 Reference Materials button."""
    query = update.callback_query
    if not query:
        return
    await query.answer()

    text = "📚 *Reference Materials*\n\nChoose category:"
    reply_markup = get_student_reference_menu_keyboard()
    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def student_reference_subcat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Processes subcategory selection for Reference Materials."""
    query = update.callback_query
    if not query or not query.data:
        return
    await query.answer()

    subcat_idx = int(query.data.split(":", 1)[1])
    subcategory = REF_SUBCATS[subcat_idx]

    if subcat_idx == 0:  # Bridge Course
        text = f"📚 *Reference Materials → {subcategory}*\n\nSelect option:"
        reply_markup = get_student_reference_bridge_keyboard()
        await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        back_cb = "sref_back_sub"
        resources = get_reference_resources(subcategory)
        await _deliver_student_document(update, context, resources, back_cb, "Reference Material")


async def student_reference_subsub_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Processes sub-subcategory selection for Bridge Course."""
    query = update.callback_query
    if not query or not query.data:
        return
    await query.answer()

    parts = query.data.split(":")
    subsub_idx = int(parts[2])
    sub_subcategory = REF_BRIDGE_SUB_SUBCATS[subsub_idx]

    if subsub_idx == 0:  # Previous Year Papers -> Select Year
        years = get_reference_available_years("Bridge Course", sub_subcategory)
        if not years:
            text = f"📚 *Resource Not Available*\n\nNo previous year papers available for Bridge Course."
            reply_markup = get_student_reference_bridge_keyboard()
            await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
            return

        text = f"🗓 *Bridge Course → Previous Year Papers*\n\nSelect Year:"
        reply_markup = get_student_reference_years_keyboard(subsub_idx, years)
        await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        back_cb = "sref_subsub:0:0"
        resources = get_reference_resources("Bridge Course", sub_subcategory=sub_subcategory)
        await _deliver_student_document(update, context, resources, back_cb, "Reference Material")


async def student_reference_yr_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Processes year selection for Bridge Course Previous Year Papers."""
    query = update.callback_query
    if not query or not query.data:
        return
    await query.answer()

    parts = query.data.split(":")
    subsub_idx = int(parts[2])
    year = int(parts[3])
    sub_subcategory = REF_BRIDGE_SUB_SUBCATS[subsub_idx]

    back_cb = "sref_subsub:0:0"
    resources = get_reference_resources("Bridge Course", sub_subcategory=sub_subcategory, year=year)
    await _deliver_student_document(update, context, resources, back_cb, "Reference Material")


async def student_reference_back_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles Back navigation for Reference Materials."""
    query = update.callback_query
    if not query or not query.data:
        return
    await query.answer()

    data = query.data
    if data == "sref_back_sub":
        text = "📚 *Reference Materials*\n\nChoose category:"
        reply_markup = get_student_reference_menu_keyboard()
        await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")

    elif data.startswith("sref_back_subsub:"):
        text = "📚 *Reference Materials → Bridge Course*\n\nSelect option:"
        reply_markup = get_student_reference_bridge_keyboard()
        await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
