"""
config.py

This module is responsible for loading environment configuration variables
from the `.env` file using `python-dotenv`.

Centralizing configuration here prevents hardcoding sensitive values
(like API keys or bot tokens) directly in the source code.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file into os.environ
load_dotenv()

# Retrieve Telegram Bot Token from environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN or BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN":
    print("Warning: BOT_TOKEN is not configured or using default placeholder in .env file.")
