"""
app/handlers/basic.py

Contains basic command and callback handlers for the IRIS Telegram bot (/start, /help, /admin, admin sub-panels, and main menu callback).
"""

from telegram import Update
from telegram.ext import CallbackQueryHandler, ContextTypes, ConversationHandler, MessageHandler, filters

import config
from app.nlp.processor import NLPResult, NLPStatus, process_query
from app.services.admin_service import get_admin, is_admin
from app.services.resource_service import (
    get_lab_manuals_resources,
    get_notes_resources,
    get_placement_resources,
    get_projects_resources,
    get_qp_resources,
    get_recent_resources,
    get_reference_resources,
    get_resource_statistics,
    get_subjects_by_semester,
)
from app.utils.expiration import register_activity_and_track
from app.utils.keyboard import (
    get_about_keyboard,
    get_admin_back_keyboard,
    get_admin_menu_keyboard,
    get_contact_admin_keyboard,
    get_help_keyboard,
    get_main_menu_keyboard,
    get_search_prompt_keyboard,
    get_search_result_keyboard,
)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler function for the /start command.
    Sends a welcome message and attaches the IRIS Main Menu keyboard.
    """
    if update.message:
        welcome_text = (
            "🎓 Welcome to IRIS\n\n"
            "Your Academic Resource Assistant\n\n"
            "Choose an option below."
        )
        msg = await update.message.reply_text(
            welcome_text,
            reply_markup=get_main_menu_keyboard()
        )
        register_activity_and_track(update, context, bot_message=msg)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler function for the /help command.
    Sends a list of available commands back to the user when they type /help.
    """
    if update.message:
        await update.message.reply_text(
            "Here are the available commands:\n\n"
            "/start - Start the bot and verify status\n"
            "/help - Display this help message\n"
            "/admin - Open administrator panel (Admins only)"
        )


async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler function for the /admin command.
    Authenticates administrators against PostgreSQL and displays the Admin Panel keyboard.
    """
    if not update.effective_user or not update.message:
        return

    telegram_id = update.effective_user.id
    admin_data = get_admin(telegram_id)

    if admin_data:
        admin_name = admin_data.get("full_name", "Admin")
        admin_text = (
            "📚 IRIS Administration\n\n"
            f"Welcome back, {admin_name}.\n\n"
            "Choose an option below."
        )
        await update.message.reply_text(
            admin_text,
            reply_markup=get_admin_menu_keyboard()
        )
    else:
        access_denied_text = (
            "❌ Access Denied\n\n"
            "You are not authorized to access the IRIS Administration Panel."
        )
        await update.message.reply_text(access_denied_text)


async def admin_view_uploads_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler for '📋 View Uploads' admin button.
    Displays the 10 most recent uploaded resources (read-only).
    """
    query = update.callback_query
    if not query or not update.effective_user:
        return

    await query.answer()
    if not is_admin(update.effective_user.id):
        await query.message.reply_text("❌ Access Denied: You are not authorized to access the IRIS Administration Panel.")
        return

    resources = get_recent_resources(limit=10)

    if not resources:
        text = "📋 *Recent Uploads*\n\nNo resources have been uploaded yet."
    else:
        text_lines = ["📋 *Recent Uploads*\n"]
        for idx, res in enumerate(resources, 1):
            title = res["title"]
            category = res["category"]
            subcategory = res.get("subcategory")
            sub_sub = res.get("sub_subcategory")
            file_name = res.get("file_name") or "document.pdf"
            uploaded_at = res.get("uploaded_at")
            time_str = uploaded_at.strftime("%d %b %Y, %H:%M") if uploaded_at else "N/A"

            cat_str = category
            if subcategory:
                cat_str += f" → {subcategory}"
            if sub_sub:
                cat_str += f" → {sub_sub}"

            num_emoji = f"{idx}️⃣" if idx <= 9 else f"{idx}."
            entry = f"{num_emoji} *{title}*\n📁 {cat_str}\n📄 `{file_name}`\n🕐 {time_str}"
            text_lines.append(entry)

        text = "\n\n".join(text_lines)

    await query.message.edit_text(
        text,
        reply_markup=get_admin_back_keyboard(),
        parse_mode="Markdown"
    )


async def admin_statistics_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler for '📊 Statistics' admin button.
    Displays a read-only aggregate overview of the IRIS repository.
    """
    query = update.callback_query
    if not query or not update.effective_user:
        return

    await query.answer()
    if not is_admin(update.effective_user.id):
        await query.message.reply_text("❌ Access Denied: You are not authorized to access the IRIS Administration Panel.")
        return

    stats = get_resource_statistics()

    if not stats:
        text = "❌ Unable to retrieve statistics from the database. Please try again."
    else:
        total_res = stats.get("total_resources", 0)
        total_subj = stats.get("total_subjects", 0)
        cat_counts = stats.get("category_counts", {})
        latest_title = stats.get("latest_title") or "None"
        latest_time = stats.get("latest_time")
        latest_str = f"{latest_title}"
        if latest_time:
            latest_str += f"\n({latest_time.strftime('%d %b %Y, %H:%M')})"

        cat_lines = []
        for cat, count in cat_counts.items():
            cat_lines.append(f"• {cat}: `{count}`")

        cat_text = "\n".join(cat_lines)

        text = (
            "📊 *IRIS Statistics*\n\n"
            f"📚 *Total Resources:* `{total_res}`\n\n"
            "📁 *Resources by Category:*\n"
            f"{cat_text}\n\n"
            f"📖 *Total Subjects:* `{total_subj}`\n\n"
            f"🕐 *Latest Upload:*\n`{latest_str}`"
        )

    await query.message.edit_text(
        text,
        reply_markup=get_admin_back_keyboard(),
        parse_mode="Markdown"
    )


async def admin_settings_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler for '⚙️ Settings' admin button.
    Displays read-only system status information.
    """
    query = update.callback_query
    if not query or not update.effective_user:
        return

    await query.answer()
    if not is_admin(update.effective_user.id):
        await query.message.reply_text("❌ Access Denied: You are not authorized to access the IRIS Administration Panel.")
        return

    admin_data = get_admin(update.effective_user.id)
    admin_name = admin_data.get("full_name", "Authenticated Admin") if admin_data else "Authenticated Admin"

    repo_status = "🟢 Configured" if config.REPOSITORY_CHANNEL_ID else "🔴 Not Configured"

    stats = get_resource_statistics()
    res_count = stats.get("total_resources", 0)
    subj_count = stats.get("total_subjects", 0)

    text = (
        "⚙️ *IRIS System Status*\n\n"
        "🟢 *Database*\nConnected\n\n"
        f"{repo_status} *Repository Channel*\n"
        f"`{config.REPOSITORY_CHANNEL_ID or 'Not Set'}`\n\n"
        "🤖 *Bot*\nOperational\n\n"
        f"👤 *Administrator*\n{admin_name}\n\n"
        f"📚 *Resources:* `{res_count}`\n"
        f"📖 *Subjects:* `{subj_count}`"
    )

    await query.message.edit_text(
        text,
        reply_markup=get_admin_back_keyboard(),
        parse_mode="Markdown"
    )


async def admin_back_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler for '⬅ Back' button to return to the Admin Panel home screen.
    """
    query = update.callback_query
    if not query or not update.effective_user:
        return

    await query.answer()
    if not is_admin(update.effective_user.id):
        await query.message.reply_text("❌ Access Denied: You are not authorized to access the IRIS Administration Panel.")
        return

    admin_data = get_admin(update.effective_user.id)
    admin_name = admin_data.get("full_name", "Admin") if admin_data else "Admin"

    admin_text = (
        "📚 IRIS Administration\n\n"
        f"Welcome back, {admin_name}.\n\n"
        "Choose an option below."
    )
    await query.message.edit_text(
        admin_text,
        reply_markup=get_admin_menu_keyboard()
    )


async def admin_back_to_main_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler for '⬅ Back to Main Menu' button to return to the student main menu.
    """
    query = update.callback_query
    if query:
        await query.answer()
        welcome_text = (
            "🎓 Welcome to IRIS\n\n"
            "Your Academic Resource Assistant\n\n"
            "Choose an option below."
        )
        await query.message.edit_text(
            welcome_text,
            reply_markup=get_main_menu_keyboard()
        )


async def contact_admin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler for '📞 Contact Admin' student main menu button.
    Displays formal contact message and inline URL link to administrator's Telegram profile.
    """
    query = update.callback_query
    if not query:
        return
    await query.answer()

    text = (
        "📞 *Contact Admin*\n\n"
        "For assistance with academic resources or the IRIS system, please contact the administrator.\n\n"
        "👤 *@raspu1in*"
    )
    reply_markup = get_contact_admin_keyboard()
    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def student_help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler for '❓ Help' student main menu button and callback.
    Displays concise guide on how to use IRIS.
    """
    query = update.callback_query
    if query:
        await query.answer()

    text = (
        "❓ *How to Use IRIS*\n\n"
        "1. Select the required resource category from the main menu.\n\n"
        "2. Follow the available options such as semester, subject, year, or module.\n\n"
        "3. Select the required resource.\n\n"
        "4. IRIS will retrieve and send the document.\n\n"
        "5. Use 🧮 CGPA to calculate SGPA or CGPA using the KTU MCA grading scale.\n\n"
        "6. Use 🔎 Search to find resources using natural-language queries.\n\n"
        "For assistance, use 📞 Contact Admin."
    )
    reply_markup = get_help_keyboard()

    if query and query.message:
        await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    elif update.message:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def about_iris_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler for 'ℹ️ About IRIS' student main menu button.
    Displays concise project information, technologies, repository architecture, and developer contact.
    """
    query = update.callback_query
    if query:
        await query.answer()

    text = (
        "ℹ️ *About IRIS*\n\n"
        "🎓 *IRIS*\n"
        "Academic Resource Assistant\n\n"
        "IRIS is a Telegram-based academic resource retrieval system designed to provide students with organized and convenient access to academic materials.\n\n"
        "📚 *Resources*\n"
        "Question Papers • Notes • Lab Manuals\n"
        "Projects • Placement Materials • Reference Materials\n\n"
        "⚙️ *Technology*\n"
        "Python • PostgreSQL • Telegram Bot API\n\n"
        "🗄️ *Repository*\n"
        "Private Telegram Repository Channel\n\n"
        "👨‍💻 *Developer*\n"
        "[@raspu1in](https://t.me/raspu1in)\n\n"
        "🔖 *Version*\n"
        "IRIS v1.0"
    )
    reply_markup = get_about_keyboard()

    if query and query.message:
        await query.message.edit_text(
            text,
            reply_markup=reply_markup,
            parse_mode="Markdown",
            disable_web_page_preview=True,
        )
    elif update.message:
        await update.message.reply_text(
            text,
            reply_markup=reply_markup,
            parse_mode="Markdown",
            disable_web_page_preview=True,
        )


async def menu_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler function for processing main menu inline keyboard button presses.
    Answers the callback query immediately to stop the loading animation,
    and sends a 'Coming Soon 🚧' reply message.
    """
    query = update.callback_query
    if query:
        await query.answer()
        if query.message:
            await query.message.reply_text("Coming Soon 🚧")


# ==============================================================================
# PHASE 8 STEP 5 — SEARCH → NLP DIAGNOSTIC INTEGRATION
# ==============================================================================

STATE_SEARCH_WAITING = 80


def format_nlp_diagnostic_message(query_text: str, result: NLPResult) -> str:
    """Formats NLPResult into a clear diagnostic Telegram Markdown message."""
    lines = [
        "🔎 *IRIS Search (Diagnostic Mode)*\n",
        f"💬 *Query*: _{query_text}_\n",
        f"⚙️ *Status*: `{result.status.value}`\n",
    ]

    if result.status == NLPStatus.VALID:
        lines.append("✅ *Query Successfully Understood!*\n")
        if result.category:
            lines.append(f"• *Category*: {result.category}")
        if result.subcategory:
            lines.append(f"• *Subcategory*: {result.subcategory}")
        if result.sub_subcategory:
            lines.append(f"• *Sub-subcategory*: {result.sub_subcategory}")
        if result.semester:
            lines.append(f"• *Semester*: {result.semester}")
        if result.subject_name:
            lines.append(f"• *Subject*: {result.subject_name}")
        elif result.subject_code:
            lines.append(f"• *Subject Code*: {result.subject_code}")
        if result.module:
            lines.append(f"• *Module*: {result.module}")
        if result.year:
            lines.append(f"• *Year*: {result.year}")
        if result.internal_exam:
            lines.append(f"• *Internal Exam*: {result.internal_exam}")

    elif result.status == NLPStatus.INCOMPLETE:
        lines.append("⚠️ *Incomplete Query*\n")
        if result.missing_fields:
            missing_str = ", ".join(f"`{f}`" for f in result.missing_fields)
            lines.append(f"• *Missing Parameters*: {missing_str}")
        if result.reason:
            lines.append(f"• *Details*: {result.reason}")

    elif result.status == NLPStatus.AMBIGUOUS:
        lines.append("🤔 *Ambiguous Query*\n")
        if result.ambiguous_field:
            lines.append(f"• *Ambiguous Field*: `{result.ambiguous_field}`")
        if result.ambiguous_candidates:
            candidates_str = "\n  - " + "\n  - ".join(result.ambiguous_candidates)
            lines.append(f"• *Possible Candidates*:{candidates_str}")
        if result.reason:
            lines.append(f"• *Details*: {result.reason}")

    elif result.status == NLPStatus.UNSUPPORTED:
        lines.append("🚫 *Unsupported Request*\n")
        lines.append("IRIS Search supports academic resource queries only.")
        if result.reason:
            lines.append(f"• *Details*: {result.reason}")

    elif result.status == NLPStatus.NO_RESOURCE_QUERY:
        lines.append("💬 *Non-Resource Query*\n")
        lines.append("No academic resource request detected in input.")
        if result.reason:
            lines.append(f"• *Details*: {result.reason}")

    elif result.status == NLPStatus.ERROR:
        lines.append("❌ *Processing Error*\n")
        lines.append("An internal error occurred while analyzing the query.")

    return "\n".join(lines)


async def search_prompt_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Entry point for 🔍 Search button.
    Prompts the student to type an academic resource query.
    """
    query = update.callback_query
    if query:
        await query.answer()

    text = (
        "🔎 *IRIS Search*\n\n"
        "Please type your academic resource query below.\n\n"
        "_Examples_:\n"
        "• `S3 DBMS module 2 notes`\n"
        "• `S2 DAA question paper 2025`\n"
        "• `Mini project report template`\n"
        "• `S1 Web Dev Lab record sample`"
    )
    reply_markup = get_search_prompt_keyboard()

    if query and query.message:
        msg = await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
        register_activity_and_track(update, context, bot_message=msg)
    elif update.message:
        msg = await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
        register_activity_and_track(update, context, bot_message=msg)

    return STATE_SEARCH_WAITING


def fetch_resources_for_nlp_result(result: NLPResult) -> list:
    """
    Adapter function mapping a VALID NLPResult to the authoritative resource_service.py retrieval functions.
    """
    if result.status != NLPStatus.VALID or not result.category:
        return []

    cat = result.category

    # 1. QUESTION PAPERS
    if cat == "Question Papers":
        if not result.subcategory or not result.semester or not result.subject_code:
            return []
        subjects = get_subjects_by_semester(result.semester)
        subj = next((s for s in subjects if s["subject_code"] == result.subject_code), None)
        if not subj:
            return []
        return get_qp_resources(
            subcategory=result.subcategory,
            semester=result.semester,
            subject_id=subj["id"],
            year=result.year,
            internal_exam=result.internal_exam,
        )

    # 2. NOTES
    elif cat == "Notes":
        if not result.semester or not result.subject_code or result.module is None:
            return []
        subjects = get_subjects_by_semester(result.semester)
        subj = next((s for s in subjects if s["subject_code"] == result.subject_code), None)
        if not subj:
            return []
        return get_notes_resources(
            semester=result.semester,
            subject_id=subj["id"],
            module=result.module,
        )

    # 3. LAB MANUALS
    elif cat == "Lab Manuals":
        if not result.subcategory or not result.semester or not result.subject_code:
            return []
        subjects = get_subjects_by_semester(result.semester)
        subj = next((s for s in subjects if s["subject_code"] == result.subject_code), None)
        if not subj:
            return []
        return get_lab_manuals_resources(
            subcategory=result.subcategory,
            semester=result.semester,
            subject_id=subj["id"],
            year=result.year,
        )

    # 4. PROJECTS (Project year is NOT passed to get_projects_resources)
    elif cat == "Projects":
        if not result.subcategory or not result.sub_subcategory:
            return []
        return get_projects_resources(
            subcategory=result.subcategory,
            sub_subcategory=result.sub_subcategory,
        )

    # 5. PLACEMENT MATERIALS
    elif cat == "Placement Materials":
        if not result.subcategory:
            return []
        return get_placement_resources(
            subcategory=result.subcategory,
        )

    # 6. REFERENCE MATERIALS
    elif cat == "Reference Materials":
        if not result.subcategory:
            return []
        return get_reference_resources(
            subcategory=result.subcategory,
            sub_subcategory=result.sub_subcategory,
            year=result.year,
        )

    return []


async def search_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handles student text query input while in Search mode.
    Passes text query to process_query().
    If VALID, queries existing resource_service.py and delivers document via Telegram repository file ID.
    Otherwise, presents the diagnostic/explanatory response.
    """
    if not update.message or not update.message.text:
        return STATE_SEARCH_WAITING

    query_text = update.message.text.strip()
    result = process_query(query_text)

    # If NOT VALID, present diagnostic response (Step 5 flow; no DB query performed)
    if result.status != NLPStatus.VALID:
        text = format_nlp_diagnostic_message(query_text, result)
        reply_markup = get_search_result_keyboard()
        msg = await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
        register_activity_and_track(update, context, bot_message=msg)
        return ConversationHandler.END

    # For VALID NLPResult: query existing resource_service.py via adapter mapping
    try:
        resources = fetch_resources_for_nlp_result(result)
    except Exception as err:
        print(f"Error fetching resources for Search query '{query_text}': {err}")
        resources = []

    chat_id = update.effective_chat.id if update.effective_chat else update.message.chat_id

    # Handle No Result Found case safely
    if not resources:
        subject_str = f" | Subject: {result.subject_name}" if result.subject_name else ""
        text = (
            "📄 *Resource Not Available*\n\n"
            f"No resources matching your query were found in the IRIS database.\n\n"
            f"💬 *Query*: _{query_text}_\n"
            f"⚙️ *Category*: {result.category}{subject_str}\n\n"
            "Please check back later or try another query."
        )
        reply_markup = get_search_result_keyboard()
        msg = await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
        register_activity_and_track(update, context, bot_message=msg)
        return ConversationHandler.END

    # Matching resource found: deliver first matching resource via existing file delivery path
    resource = resources[0]
    file_id = resource.get("telegram_file_id")

    if not file_id:
        text = (
            "⚠️ *Resource Error*\n\n"
            "The resource exists in the database, but its stored Telegram file reference is unavailable.\n\n"
            "Please contact the administrator."
        )
        reply_markup = get_search_result_keyboard()
        msg = await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
        register_activity_and_track(update, context, bot_message=msg)
        return ConversationHandler.END

    try:
        caption = f"📄 {resource['title']}"
        await context.bot.send_document(
            chat_id=chat_id,
            document=file_id,
            caption=caption,
        )
        text = f"✅ *{result.category} Delivered!*\n\n📌 *{resource['title']}*"
        reply_markup = get_search_result_keyboard()
        msg = await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
        register_activity_and_track(update, context, bot_message=msg)
    except Exception as error:
        print(f"Error delivering Telegram document {file_id}: {error}")
        text = (
            "⚠️ *Delivery Error*\n\n"
            "Failed to send document from Telegram repository. Please try again later."
        )
        reply_markup = get_search_result_keyboard()
        msg = await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
        register_activity_and_track(update, context, bot_message=msg)

    return ConversationHandler.END


async def search_cancel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Cancels Search mode and returns to student main menu.
    """
    query = update.callback_query
    if query:
        await query.answer()
        text = (
            "🎓 *IRIS*\n"
            "Your Academic Resource Assistant\n\n"
            "Choose an option below."
        )
        await query.message.edit_text(text, reply_markup=get_main_menu_keyboard(), parse_mode="Markdown")

    return ConversationHandler.END


def get_search_conversation_handler() -> ConversationHandler:
    """
    Constructs ConversationHandler for student Search mode -> NLP query processing.
    """
    return ConversationHandler(
        entry_points=[
            CallbackQueryHandler(search_prompt_handler, pattern="^search$"),
        ],
        states={
            STATE_SEARCH_WAITING: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, search_query_handler),
            ],
        },
        fallbacks=[
            CallbackQueryHandler(search_cancel_handler, pattern="^student_back_to_main$"),
            CallbackQueryHandler(search_prompt_handler, pattern="^search$"),
        ],
        allow_reentry=True,
    )


