# IRIS

IRIS is a Telegram Bot project built with Python using `python-telegram-bot` and `python-dotenv`.

## Project Foundation & Directory Structure

```text
IRIS/
│
├── run.py             # Single application entry point
├── config.py          # Configuration module: loads environment variables securely
├── requirements.txt   # Project dependencies list
├── .env               # Local environment variables (do NOT commit secrets)
├── .env.example       # Template for environment variables
├── .gitignore         # Rules for files and folders git should ignore
├── README.md          # Project documentation
│
├── app/               # Main application package containing modular components
│   ├── main.py        # Application initialization, handler registration, and main()
│   ├── handlers/      # Command and message handler modules
│   ├── services/      # Business logic and external integration services
│   ├── database/      # Database interfaces and models
│   ├── utils/         # Helper functions and utilities
│   └── __init__.py    # Marks app directory as a Python package
│
├── data/              # Storage directory for data assets
│   ├── documents/     # Raw document files
│   ├── processed/     # Processed data files
│   └── vector_store/  # Storage for embeddings / vector data
│
└── logs/              # Application execution logs
```

## How to Setup and Run

1. **Activate Virtual Environment** (if not already activated):
   - Windows (PowerShell): `.\venv\Scripts\Activate.ps1`
   - Linux / macOS: `source venv/bin/activate`

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   Update your `.env` file with your actual Telegram Bot Token from [@BotFather](https://t.me/BotFather):
   ```env
   BOT_TOKEN=123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ
   ```

4. **Start the Bot**:
   ```bash
   python run.py
   ```
