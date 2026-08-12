"""
app/handlers/admin_upload.py

Handler module for the Administrator Resource Upload Wizard.
Implements a stateful ConversationHandler flow for uploading academic resources.
"""

from typing import Any, Dict, Optional
from telegram import Update
from telegram.ext import (
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

import config
from app.services.admin_service import is_admin
from app.services.resource_service import (
    create_resource,
    get_subject_by_id,
    get_subjects_by_semester,
)
from app.utils.keyboard import (
    get_admin_menu_keyboard,
    get_upload_categories_keyboard,
    get_upload_document_prompt_keyboard,
    get_upload_internals_keyboard,
    get_upload_modules_keyboard,
    get_upload_semesters_keyboard,
    get_upload_sub_subcategories_keyboard,
    get_upload_subcategories_keyboard,
    get_upload_subjects_keyboard,
    get_upload_years_keyboard,
)
from app.utils.taxonomy import TAXONOMY, generate_title

# Conversation States
(
    STATE_CATEGORY,
    STATE_SUBCATEGORY,
    STATE_SUB_SUBCATEGORY,
    STATE_SEMESTER,
    STATE_YEAR,
    STATE_INTERNAL,
    STATE_SUBJECT,
    STATE_MODULE,
    STATE_WAITING_DOCUMENT,
) = range(9)


def _init_upload_data(context: ContextTypes.DEFAULT_TYPE) -> Dict[str, Any]:
    """Initializes or resets upload session state in context.user_data."""
    context.user_data["upload"] = {
        "category": None,
        "subcategory": None,
        "sub_subcategory": None,
        "semester": None,
        "year": None,
        "internal_exam": None,
        "subject_id": None,
        "module": None,
        "history": [],  # Stack of (state, prompt_text, reply_markup) for Back navigation
    }
    return context.user_data["upload"]


def _push_history(context: ContextTypes.DEFAULT_TYPE, state: int, text: str, reply_markup: Any) -> None:
    """Pushes current screen info to history stack."""
    upload = context.user_data.get("upload")
    if upload is not None:
        upload["history"].append({
            "state": state,
            "text": text,
            "reply_markup": reply_markup,
        })


async def start_upload_wizard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Entry point for 📤 Upload Resource button."""
    query = update.callback_query
    if not query:
        return ConversationHandler.END

    await query.answer()
    user_id = query.from_user.id
    if not is_admin(user_id):
        await query.message.reply_text("❌ Access Denied: Administrator privileges required.")
        return ConversationHandler.END

    _init_upload_data(context)

    prompt_text = "📤 *Upload Resource Wizard*\n\nStep 1: Choose a category:"
    reply_markup = get_upload_categories_keyboard()

    _push_history(context, STATE_CATEGORY, prompt_text, reply_markup)
    await query.message.edit_text(prompt_text, reply_markup=reply_markup, parse_mode="Markdown")
    return STATE_CATEGORY


async def handle_category_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Processes category button click."""
    query = update.callback_query
    if not query or not query.data:
        return STATE_CATEGORY
    await query.answer()

    category = query.data.split(":", 1)[1]
    upload = context.user_data.get("upload", _init_upload_data(context))
    upload["category"] = category

    subcats = TAXONOMY.get(category, {}).get("subcategories", [])

    if subcats:
        prompt_text = f"📄 *{category}*\n\nChoose subcategory:"
        reply_markup = get_upload_subcategories_keyboard(category)
        _push_history(context, STATE_SUBCATEGORY, prompt_text, reply_markup)
        await query.message.edit_text(prompt_text, reply_markup=reply_markup, parse_mode="Markdown")
        return STATE_SUBCATEGORY
    else:
        # Category has no subcategories (e.g., Notes)
        if category == "Notes":
            prompt_text = "📝 *Notes*\n\nSelect Semester:"
            reply_markup = get_upload_semesters_keyboard()
            _push_history(context, STATE_SEMESTER, prompt_text, reply_markup)
            await query.message.edit_text(prompt_text, reply_markup=reply_markup, parse_mode="Markdown")
            return STATE_SEMESTER

    prompt_text = f"📤 *{category}*\n\n📎 Please send the PDF/document for this resource."
    reply_markup = get_upload_document_prompt_keyboard()
    _push_history(context, STATE_WAITING_DOCUMENT, prompt_text, reply_markup)
    await query.message.edit_text(prompt_text, reply_markup=reply_markup, parse_mode="Markdown")
    return STATE_WAITING_DOCUMENT


async def handle_subcategory_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Processes subcategory button click."""
    query = update.callback_query
    if not query or not query.data:
        return STATE_SUBCATEGORY
    await query.answer()

    subcategory = query.data.split(":", 1)[1]
    upload = context.user_data["upload"]
    upload["subcategory"] = subcategory
    category = upload["category"]

    sub_subcats = TAXONOMY.get(category, {}).get("sub_subcategories", {}).get(subcategory, [])

    # Internal Examination question papers require Semester -> Year -> Internal Exam -> Subject flow
    if sub_subcats and not (category == "Question Papers" and subcategory == "Internal Examination"):
        prompt_text = f"📁 *{category} → {subcategory}*\n\nSelect option:"
        reply_markup = get_upload_sub_subcategories_keyboard(category, subcategory)
        _push_history(context, STATE_SUB_SUBCATEGORY, prompt_text, reply_markup)
        await query.message.edit_text(prompt_text, reply_markup=reply_markup, parse_mode="Markdown")
        return STATE_SUB_SUBCATEGORY

    # Check if semester selection is required for this subcategory
    if category in ["Question Papers", "Lab Manuals"]:
        prompt_text = f"📁 *{category} → {subcategory}*\n\nSelect Semester:"
        reply_markup = get_upload_semesters_keyboard()
        _push_history(context, STATE_SEMESTER, prompt_text, reply_markup)
        await query.message.edit_text(prompt_text, reply_markup=reply_markup, parse_mode="Markdown")
        return STATE_SEMESTER

    # For Standalone Reference Materials or Placement Materials
    prompt_text = f"📤 *{category} → {subcategory}*\n\n📎 Please send the PDF/document for this resource."
    reply_markup = get_upload_document_prompt_keyboard()
    _push_history(context, STATE_WAITING_DOCUMENT, prompt_text, reply_markup)
    await query.message.edit_text(prompt_text, reply_markup=reply_markup, parse_mode="Markdown")
    return STATE_WAITING_DOCUMENT


async def handle_sub_subcategory_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Processes sub-subcategory button click."""
    query = update.callback_query
    if not query or not query.data:
        return STATE_SUB_SUBCATEGORY
    await query.answer()

    sub_subcategory = query.data.split(":", 1)[1]
    upload = context.user_data["upload"]
    upload["sub_subcategory"] = sub_subcategory
    category = upload["category"]
    subcategory = upload["subcategory"]

    if category == "Reference Materials" and subcategory == "Bridge Course" and sub_subcategory == "Previous Year Papers":
        prompt_text = f"📚 *Bridge Course → Previous Year Papers*\n\nSelect Year:"
        reply_markup = get_upload_years_keyboard()
        _push_history(context, STATE_YEAR, prompt_text, reply_markup)
        await query.message.edit_text(prompt_text, reply_markup=reply_markup, parse_mode="Markdown")
        return STATE_YEAR

    # For Projects or other template options
    prompt_text = f"📤 *{category} → {subcategory} → {sub_subcategory}*\n\n📎 Please send the PDF/document for this resource."
    reply_markup = get_upload_document_prompt_keyboard()
    _push_history(context, STATE_WAITING_DOCUMENT, prompt_text, reply_markup)
    await query.message.edit_text(prompt_text, reply_markup=reply_markup, parse_mode="Markdown")
    return STATE_WAITING_DOCUMENT


async def handle_semester_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Processes semester selection (1-4)."""
    query = update.callback_query
    if not query or not query.data:
        return STATE_SEMESTER
    await query.answer()

    semester = int(query.data.split(":", 1)[1])
    upload = context.user_data["upload"]
    upload["semester"] = semester
    category = upload["category"]
    subcategory = upload.get("subcategory")

    # If Year is required before subject/internal selection
    if (category == "Question Papers" and subcategory in ["Semester Examination", "Internal Examination"]) or \
       (category == "Lab Manuals" and subcategory == "Lab Question Papers"):
        prompt_text = f"🗓 *{category} → {subcategory} (Semester {semester})*\n\nSelect Year:"
        reply_markup = get_upload_years_keyboard()
        _push_history(context, STATE_YEAR, prompt_text, reply_markup)
        await query.message.edit_text(prompt_text, reply_markup=reply_markup, parse_mode="Markdown")
        return STATE_YEAR

    # Otherwise fetch subjects for semester
    subjects = get_subjects_by_semester(semester)
    if not subjects:
        prompt_text = f"⚠️ No subjects found for Semester {semester}."
        reply_markup = get_upload_semesters_keyboard()
        await query.message.edit_text(prompt_text, reply_markup=reply_markup, parse_mode="Markdown")
        return STATE_SEMESTER

    header = f"{category} → {subcategory}" if subcategory else category
    prompt_text = f"📚 *{header} (Semester {semester})*\n\nSelect Subject:"
    reply_markup = get_upload_subjects_keyboard(subjects)
    _push_history(context, STATE_SUBJECT, prompt_text, reply_markup)
    await query.message.edit_text(prompt_text, reply_markup=reply_markup, parse_mode="Markdown")
    return STATE_SUBJECT


async def handle_year_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Processes year selection."""
    query = update.callback_query
    if not query or not query.data:
        return STATE_YEAR
    await query.answer()

    year = int(query.data.split(":", 1)[1])
    upload = context.user_data["upload"]
    upload["year"] = year
    category = upload["category"]
    subcategory = upload.get("subcategory")
    semester = upload.get("semester")

    # If Question Papers -> Internal Examination, prompt for First / Second Internal
    if category == "Question Papers" and subcategory == "Internal Examination":
        prompt_text = f"📝 *Internal Examination ({year})*\n\nSelect Internal Exam:"
        reply_markup = get_upload_internals_keyboard()
        _push_history(context, STATE_INTERNAL, prompt_text, reply_markup)
        await query.message.edit_text(prompt_text, reply_markup=reply_markup, parse_mode="Markdown")
        return STATE_INTERNAL

    # If Reference Materials -> Bridge Course -> Previous Year Papers
    if category == "Reference Materials" and subcategory == "Bridge Course":
        prompt_text = f"📤 *Bridge Course → Previous Year Papers ({year})*\n\n📎 Please send the PDF/document for this resource."
        reply_markup = get_upload_document_prompt_keyboard()
        _push_history(context, STATE_WAITING_DOCUMENT, prompt_text, reply_markup)
        await query.message.edit_text(prompt_text, reply_markup=reply_markup, parse_mode="Markdown")
        return STATE_WAITING_DOCUMENT

    # Otherwise fetch subjects for semester
    subjects = get_subjects_by_semester(semester)
    prompt_text = f"📚 *{category} → {subcategory} (Sem {semester}, {year})*\n\nSelect Subject:"
    reply_markup = get_upload_subjects_keyboard(subjects)
    _push_history(context, STATE_SUBJECT, prompt_text, reply_markup)
    await query.message.edit_text(prompt_text, reply_markup=reply_markup, parse_mode="Markdown")
    return STATE_SUBJECT


async def handle_internal_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Processes internal exam selection (First/Second Internal)."""
    query = update.callback_query
    if not query or not query.data:
        return STATE_INTERNAL
    await query.answer()

    internal_str = query.data.split(":", 1)[1]
    upload = context.user_data["upload"]
    upload["sub_subcategory"] = internal_str
    upload["internal_exam"] = 1 if internal_str == "First Internal" else 2

    semester = upload["semester"]
    subjects = get_subjects_by_semester(semester)
    prompt_text = f"📚 *Internal Exam: {internal_str} (Sem {semester})*\n\nSelect Subject:"
    reply_markup = get_upload_subjects_keyboard(subjects)
    _push_history(context, STATE_SUBJECT, prompt_text, reply_markup)
    await query.message.edit_text(prompt_text, reply_markup=reply_markup, parse_mode="Markdown")
    return STATE_SUBJECT


async def handle_subject_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Processes subject selection."""
    query = update.callback_query
    if not query or not query.data:
        return STATE_SUBJECT
    await query.answer()

    subject_id = int(query.data.split(":", 1)[1])
    upload = context.user_data["upload"]
    upload["subject_id"] = subject_id
    category = upload["category"]

    subject = get_subject_by_id(subject_id)
    subject_name = subject["subject_name"] if subject else "Subject"

    if category == "Notes":
        prompt_text = f"📝 *Notes → {subject_name}*\n\nSelect Module:"
        reply_markup = get_upload_modules_keyboard()
        _push_history(context, STATE_MODULE, prompt_text, reply_markup)
        await query.message.edit_text(prompt_text, reply_markup=reply_markup, parse_mode="Markdown")
        return STATE_MODULE

    prompt_text = f"📤 *Selected Subject:* {subject_name}\n\n📎 Please send the PDF/document for this resource."
    reply_markup = get_upload_document_prompt_keyboard()
    _push_history(context, STATE_WAITING_DOCUMENT, prompt_text, reply_markup)
    await query.message.edit_text(prompt_text, reply_markup=reply_markup, parse_mode="Markdown")
    return STATE_WAITING_DOCUMENT


async def handle_module_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Processes module selection (1-5)."""
    query = update.callback_query
    if not query or not query.data:
        return STATE_MODULE
    await query.answer()

    module = int(query.data.split(":", 1)[1])
    upload = context.user_data["upload"]
    upload["module"] = module

    prompt_text = f"📤 *Notes → Module {module}*\n\n📎 Please send the PDF/document for this resource."
    reply_markup = get_upload_document_prompt_keyboard()
    _push_history(context, STATE_WAITING_DOCUMENT, prompt_text, reply_markup)
    await query.message.edit_text(prompt_text, reply_markup=reply_markup, parse_mode="Markdown")
    return STATE_WAITING_DOCUMENT


async def handle_document_upload(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles receiving the document/PDF file from the administrator."""
    if not update.message or not update.message.document:
        await update.message.reply_text("⚠️ Please upload a valid document or PDF file.")
        return STATE_WAITING_DOCUMENT

    upload = context.user_data.get("upload")
    if not upload:
        await update.message.reply_text("❌ Upload session expired. Please start again with /admin.")
        return ConversationHandler.END

    category = upload.get("category")
    subcategory = upload.get("subcategory")

    # Validate required metadata for Question Papers -> Internal Examination
    if category == "Question Papers" and subcategory == "Internal Examination":
        missing = []
        if not upload.get("semester"):
            missing.append("Semester")
        if not upload.get("year"):
            missing.append("Year")
        if not upload.get("internal_exam") or not upload.get("sub_subcategory"):
            missing.append("Internal Examination")
        if not upload.get("subject_id"):
            missing.append("Subject")
        if missing:
            err_text = f"❌ *Upload Error*: Missing required metadata ({', '.join(missing)}). Please restart with /admin."
            await update.message.reply_text(err_text, parse_mode="Markdown")
            return ConversationHandler.END

    document = update.message.document
    original_file_id = document.file_id
    file_name = document.file_name or "resource.pdf"

    # Mandatory repository channel upload check
    if not config.REPOSITORY_CHANNEL_ID:
        error_msg = (
            "❌ Upload Failed\n\n"
            "The repository channel is not configured in the application environment (REPOSITORY_CHANNEL_ID). "
            "No resource was added to the database. Please contact the system administrator."
        )
        await update.message.reply_text(
            error_msg,
            reply_markup=get_upload_document_prompt_keyboard()
        )
        return STATE_WAITING_DOCUMENT

    telegram_file_id = None
    try:
        channel_msg = await context.bot.send_document(
            chat_id=config.REPOSITORY_CHANNEL_ID,
            document=original_file_id,
            caption=f"IRIS Repository Upload: {file_name}"
        )
        if channel_msg and channel_msg.document:
            telegram_file_id = channel_msg.document.file_id
    except Exception as error:
        print(f"Error: Failed to store document in repository channel ({config.REPOSITORY_CHANNEL_ID}): {error}")

    if not telegram_file_id:
        error_msg = (
            "❌ Upload Failed\n\n"
            "The document could not be stored in the IRIS repository channel. "
            "No resource was added to the database. Please try again."
        )
        await update.message.reply_text(
            error_msg,
            reply_markup=get_upload_document_prompt_keyboard()
        )
        return STATE_WAITING_DOCUMENT

    # Retrieve subject details for title generation
    subject_id = upload.get("subject_id")
    subject_name = None
    if subject_id:
        subj_info = get_subject_by_id(subject_id)
        if subj_info:
            subject_name = subj_info["subject_name"]

    # Generate title automatically from metadata
    auto_title = generate_title(
        category=upload.get("category"),
        subcategory=upload.get("subcategory"),
        sub_subcategory=upload.get("sub_subcategory"),
        subject_name=subject_name,
        semester=upload.get("semester"),
        year=upload.get("year"),
        module=upload.get("module"),
    )

    resource_data = {
        "category": upload.get("category"),
        "subcategory": upload.get("subcategory"),
        "sub_subcategory": upload.get("sub_subcategory"),
        "subject_id": subject_id,
        "semester": upload.get("semester"),
        "year": upload.get("year"),
        "module": upload.get("module"),
        "internal_exam": upload.get("internal_exam"),
        "title": auto_title,
        "file_name": file_name,
        "telegram_file_id": telegram_file_id,
    }

    success, message, resource_id = create_resource(resource_data)

    if success:
        context.user_data["upload"] = {}
        success_text = (
            "✅ *Resource Uploaded Successfully!*\n\n"
            f"📌 *Title:* `{auto_title}`\n"
            f"📁 *Category:* {resource_data['category']}\n"
            f"📄 *File Name:* `{file_name}`\n\n"
            "Resource record has been saved to the IRIS database."
        )
        await update.message.reply_text(
            success_text,
            reply_markup=get_admin_menu_keyboard(),
            parse_mode="Markdown"
        )
        return ConversationHandler.END
    else:
        await update.message.reply_text(
            f"{message}\n\nPlease try again or cancel.",
            reply_markup=get_upload_document_prompt_keyboard()
        )
        return STATE_WAITING_DOCUMENT


async def handle_upload_back(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles ⬅ Back button click in upload wizard."""
    query = update.callback_query
    if not query:
        return ConversationHandler.END
    await query.answer()

    upload = context.user_data.get("upload")
    if not upload or not upload.get("history"):
        # No history, return to Category Selection
        _init_upload_data(context)
        prompt_text = "📤 *Upload Resource Wizard*\n\nStep 1: Choose a category:"
        reply_markup = get_upload_categories_keyboard()
        await query.message.edit_text(prompt_text, reply_markup=reply_markup, parse_mode="Markdown")
        return STATE_CATEGORY

    history = upload["history"]
    # Pop current screen
    if len(history) > 1:
        history.pop()
        prev = history[-1]
        await query.message.edit_text(prev["text"], reply_markup=prev["reply_markup"], parse_mode="Markdown")
        return prev["state"]
    else:
        _init_upload_data(context)
        prompt_text = "📤 *Upload Resource Wizard*\n\nStep 1: Choose a category:"
        reply_markup = get_upload_categories_keyboard()
        await query.message.edit_text(prompt_text, reply_markup=reply_markup, parse_mode="Markdown")
        return STATE_CATEGORY


async def handle_upload_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles ❌ Cancel button click in upload wizard."""
    query = update.callback_query
    if query:
        await query.answer()
        context.user_data["upload"] = {}
        await query.message.edit_text(
            "📚 IRIS Administration\n\nWelcome back, Rasputin.\n\nChoose an option below.",
            reply_markup=get_admin_menu_keyboard()
        )
    return ConversationHandler.END


def get_upload_conversation_handler() -> ConversationHandler:
    """Returns the configured ConversationHandler for the upload wizard."""
    return ConversationHandler(
        entry_points=[
            CallbackQueryHandler(start_upload_wizard, pattern="^admin_upload_resource$")
        ],
        states={
            STATE_CATEGORY: [
                CallbackQueryHandler(handle_category_selection, pattern="^up_cat:")
            ],
            STATE_SUBCATEGORY: [
                CallbackQueryHandler(handle_subcategory_selection, pattern="^up_subcat:")
            ],
            STATE_SUB_SUBCATEGORY: [
                CallbackQueryHandler(handle_sub_subcategory_selection, pattern="^up_subsubcat:")
            ],
            STATE_SEMESTER: [
                CallbackQueryHandler(handle_semester_selection, pattern="^up_sem:")
            ],
            STATE_YEAR: [
                CallbackQueryHandler(handle_year_selection, pattern="^up_year:")
            ],
            STATE_INTERNAL: [
                CallbackQueryHandler(handle_internal_selection, pattern="^up_internal:")
            ],
            STATE_SUBJECT: [
                CallbackQueryHandler(handle_subject_selection, pattern="^up_subj:")
            ],
            STATE_MODULE: [
                CallbackQueryHandler(handle_module_selection, pattern="^up_module:")
            ],
            STATE_WAITING_DOCUMENT: [
                MessageHandler(filters.Document.ALL, handle_document_upload)
            ],
        },
        fallbacks=[
            CallbackQueryHandler(handle_upload_back, pattern="^upload_back$"),
            CallbackQueryHandler(handle_upload_cancel, pattern="^upload_cancel$"),
        ],
        per_message=False,
        per_chat=True,
        per_user=True,
    )
