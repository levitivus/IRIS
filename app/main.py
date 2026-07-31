"""
app/main.py

Contains the main application setup logic for the IRIS Telegram bot.
Sets up the bot application, registers command handlers, and starts polling for updates.
"""

import sys
from telegram.ext import ApplicationBuilder, CommandHandler

import config
from app.handlers.basic import help_command, start_command


def main() -> None:
    """
    Initializes and starts the Telegram bot application.
    """
    if not config.BOT_TOKEN or config.BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN":
        print("Error: Please set a valid BOT_TOKEN in your .env file before starting the bot.")
        sys.exit(1)

    # Build the Application using the bot token loaded from config.py
    application = ApplicationBuilder().token(config.BOT_TOKEN).build()

    # Register command handlers from app.handlers.basic
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))

    # Start polling for incoming messages from Telegram
    print("IRIS bot is starting...")
    application.run_polling()
