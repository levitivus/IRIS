"""
app/handlers/basic.py

Contains basic command and callback handlers for the IRIS Telegram bot (/start, /help, /admin, admin sub-panels, and main menu callback).
"""

from telegram import Update
from telegram.ext import ContextTypes

import config
from app.services.admin_service import get_admin, is_admin
from app.services.resource_service import get_recent_resources, get_resource_statistics
from app.utils.expiration import register_activity_and_track
from app.utils.keyboard import (
    get_about_keyboard,
    get_admin_back_keyboard,
    get_admin_menu_keyboard,
    get_contact_admin_keyboard,
    get_help_keyboard,
    get_main_menu_keyboard,
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

