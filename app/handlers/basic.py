"""
app/handlers/basic.py

Contains basic command and callback handlers for the IRIS Telegram bot (/start, /help, and main menu callback).
"""

from telegram import Update
from telegram.ext import ContextTypes

from app.utils.keyboard import get_main_menu_keyboard


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
            "/help - Display this help message"
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
