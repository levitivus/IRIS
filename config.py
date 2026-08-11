"""
config.py

This module is responsible for loading environment configuration variables
from the `.env` file using `python-dotenv`.

Centralizing configuration here prevents hardcoding sensitive values
(like API keys, bot tokens, database credentials, or Telegram repository channel IDs)
directly in the source code.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file into os.environ
load_dotenv()

# Retrieve Telegram Bot Token from environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Retrieve PostgreSQL Database configuration variables
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "iris_bot")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# Retrieve Telegram Repository Channel ID for storing uploaded PDFs
REPOSITORY_CHANNEL_ID = os.getenv("REPOSITORY_CHANNEL_ID")

if not BOT_TOKEN or BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN":
    print("Warning: BOT_TOKEN is not configured or using default placeholder in .env file.")
