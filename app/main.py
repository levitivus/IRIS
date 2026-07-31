"""
app/main.py

Contains the main application setup logic for the IRIS Telegram bot.
Sets up the bot application, registers command handlers, and starts polling for updates.
"""

import sys
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

import config


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler function for the /start command.
    Sends a greeting message back to the user when they type /start.
    """
    if update.message:
        await update.message.reply_text("Hello!\nIRIS is online.")


def main() -> None:
    """
    Initializes and starts the Telegram bot application.
    """
    if not config.BOT_TOKEN or config.BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN":
        print("Error: Please set a valid BOT_TOKEN in your .env file before starting the bot.")
        sys.exit(1)

    # Build the Application using the bot token loaded from config.py
    application = ApplicationBuilder().token(config.BOT_TOKEN).build()

    # Register the /start command handler
    application.add_handler(CommandHandler("start", start_command))

    # Start polling for incoming messages from Telegram
    print("IRIS bot is starting...")
    application.run_polling()
