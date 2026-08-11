"""
app/main.py

Contains the main application setup logic for the IRIS Telegram bot.
Sets up the bot application, registers command handlers, upload wizard handlers, and callback query handlers, and starts polling for updates.
"""

import sys
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler

import config
from app.handlers.admin_upload import get_upload_conversation_handler
from app.handlers.basic import (
    admin_back_handler,
    admin_back_to_main_handler,
    admin_command,
    admin_settings_handler,
    admin_statistics_handler,
    admin_view_uploads_handler,
    help_command,
    menu_callback_handler,
    start_command,
)


def main() -> None:
    """
    Initializes and starts the Telegram bot application.
    """
    if not config.BOT_TOKEN or config.BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN":
        print("Error: Please set a valid BOT_TOKEN in your .env file before starting the bot.")
        sys.exit(1)

    # Build the Application using the bot token loaded from config.py
    application = ApplicationBuilder().token(config.BOT_TOKEN).build()

    # Register upload wizard conversation handler (evaluated prior to fallback callback handlers)
    application.add_handler(get_upload_conversation_handler())

    # Register command handlers from app.handlers.basic
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("admin", admin_command))

    # Register admin panel callback handlers
    application.add_handler(CallbackQueryHandler(admin_view_uploads_handler, pattern="^admin_view_uploads$"))
    application.add_handler(CallbackQueryHandler(admin_statistics_handler, pattern="^admin_statistics$"))
    application.add_handler(CallbackQueryHandler(admin_settings_handler, pattern="^admin_settings$"))
    application.add_handler(CallbackQueryHandler(admin_back_handler, pattern="^admin_back$"))
    application.add_handler(CallbackQueryHandler(admin_back_to_main_handler, pattern="^admin_back_to_main$"))

    # Register fallback callback query handler for student inline keyboard buttons
    application.add_handler(CallbackQueryHandler(menu_callback_handler))

    # Start polling for incoming messages from Telegram
    print("IRIS bot is starting...")
    application.run_polling()
