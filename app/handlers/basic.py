"""
app/handlers/basic.py

Contains basic command and callback handlers for the IRIS Telegram bot (/start, /help, /admin, and main menu callback).
"""

from telegram import Update
from telegram.ext import ContextTypes

from app.services.admin_service import get_admin
from app.utils.keyboard import get_admin_menu_keyboard, get_main_menu_keyboard


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
        await update.message.reply_text(
            welcome_text,
            reply_markup=get_main_menu_keyboard()
        )


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
