"""
app/main.py

Contains the main application setup logic for the IRIS Telegram bot.
Sets up the bot application, registers command handlers, upload wizard handlers, admin panel handlers, and student retrieval handlers (Phases 5-7), and starts polling for updates.
"""

import sys
from telegram import Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, TypeHandler

import config
from app.handlers.admin_upload import get_upload_conversation_handler
from app.handlers.cgpa import get_cgpa_conversation_handler
from app.utils.expiration import global_activity_tracker_handler
from app.handlers.basic import (
    about_iris_handler,
    admin_back_handler,
    admin_back_to_main_handler,
    admin_command,
    admin_settings_handler,
    admin_statistics_handler,
    admin_view_uploads_handler,
    contact_admin_handler,
    get_search_conversation_handler,
    help_command,
    menu_callback_handler,
    start_command,
    student_help_handler,
)
from app.handlers.student_retrieval import (
    student_lab_back_handler,
    student_lab_menu_handler,
    student_lab_sem_handler,
    student_lab_subcat_handler,
    student_lab_subj_handler,
    student_lab_yr_handler,
    student_notes_back_handler,
    student_notes_menu_handler,
    student_notes_mod_handler,
    student_notes_sem_handler,
    student_notes_subj_handler,
    student_placement_menu_handler,
    student_placement_subcat_handler,
    student_projects_back_handler,
    student_projects_item_handler,
    student_projects_menu_handler,
    student_projects_subcat_handler,
    student_qp_back_handler,
    student_qp_internal_handler,
    student_qp_menu_handler,
    student_qp_sem_handler,
    student_qp_subcat_handler,
    student_qp_subject_handler,
    student_qp_year_handler,
    student_reference_back_handler,
    student_reference_menu_handler,
    student_reference_subcat_handler,
    student_reference_subsub_handler,
    student_reference_yr_handler,
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

    # Register global inactivity tracker and temporary UI message expiration handler (group=-1)
    application.add_handler(TypeHandler(Update, global_activity_tracker_handler), group=-1)

    # Register upload wizard conversation handler (evaluated prior to fallback callback handlers)
    application.add_handler(get_upload_conversation_handler())

    # Register CGPA calculator conversation handler
    application.add_handler(get_cgpa_conversation_handler())

    # Register Search conversation handler (Phase 8 Step 5)
    application.add_handler(get_search_conversation_handler())

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

    # Register Student Question Papers retrieval callback query handlers (Phase 5)
    application.add_handler(CallbackQueryHandler(student_qp_menu_handler, pattern="^question_papers$"))
    application.add_handler(CallbackQueryHandler(student_qp_subcat_handler, pattern="^sqp_subcat:"))
    application.add_handler(CallbackQueryHandler(student_qp_sem_handler, pattern="^sqp_sem:"))
    application.add_handler(CallbackQueryHandler(student_qp_year_handler, pattern="^sqp_yr:"))
    application.add_handler(CallbackQueryHandler(student_qp_internal_handler, pattern="^sqp_int:"))
    application.add_handler(CallbackQueryHandler(student_qp_subject_handler, pattern="^sqp_subj:"))
    application.add_handler(CallbackQueryHandler(student_qp_back_handler, pattern="^sqp_back_"))

    # Register Student Notes retrieval callback query handlers (Phase 6)
    application.add_handler(CallbackQueryHandler(student_notes_menu_handler, pattern="^notes$"))
    application.add_handler(CallbackQueryHandler(student_notes_sem_handler, pattern="^snotes_sem:"))
    application.add_handler(CallbackQueryHandler(student_notes_subj_handler, pattern="^snotes_subj:"))
    application.add_handler(CallbackQueryHandler(student_notes_mod_handler, pattern="^snotes_mod:"))
    application.add_handler(CallbackQueryHandler(student_notes_back_handler, pattern="^snotes_back_"))

    # Register Student Projects retrieval callback query handlers (Phase 7)
    application.add_handler(CallbackQueryHandler(student_projects_menu_handler, pattern="^projects$"))
    application.add_handler(CallbackQueryHandler(student_projects_subcat_handler, pattern="^sproj_sub:"))
    application.add_handler(CallbackQueryHandler(student_projects_item_handler, pattern="^sproj_item:"))
    application.add_handler(CallbackQueryHandler(student_projects_back_handler, pattern="^sproj_back_"))

    # Register Student Lab Manuals retrieval callback query handlers (Phase 7)
    application.add_handler(CallbackQueryHandler(student_lab_menu_handler, pattern="^lab_manuals$"))
    application.add_handler(CallbackQueryHandler(student_lab_subcat_handler, pattern="^slab_sub:"))
    application.add_handler(CallbackQueryHandler(student_lab_sem_handler, pattern="^slab_sem:"))
    application.add_handler(CallbackQueryHandler(student_lab_yr_handler, pattern="^slab_yr:"))
    application.add_handler(CallbackQueryHandler(student_lab_subj_handler, pattern="^slab_subj:"))
    application.add_handler(CallbackQueryHandler(student_lab_back_handler, pattern="^slab_back_"))

    # Register Student Placement Materials retrieval callback query handlers (Phase 7)
    application.add_handler(CallbackQueryHandler(student_placement_menu_handler, pattern="^placement_materials$"))
    application.add_handler(CallbackQueryHandler(student_placement_subcat_handler, pattern="^splace_sub:"))

    # Register Student Reference Materials retrieval callback query handlers (Phase 7)
    application.add_handler(CallbackQueryHandler(student_reference_menu_handler, pattern="^reference_materials$"))
    application.add_handler(CallbackQueryHandler(student_reference_subcat_handler, pattern="^sref_sub:"))
    application.add_handler(CallbackQueryHandler(student_reference_subsub_handler, pattern="^sref_subsub:"))
    application.add_handler(CallbackQueryHandler(student_reference_yr_handler, pattern="^sref_yr:"))
    application.add_handler(CallbackQueryHandler(student_reference_back_handler, pattern="^sref_back_"))

    # Register Contact Admin callback query handler
    application.add_handler(CallbackQueryHandler(contact_admin_handler, pattern="^contact_admin$"))

    # Register Student Help callback query handler
    application.add_handler(CallbackQueryHandler(student_help_handler, pattern="^help$"))

    # Register About IRIS callback query handler
    application.add_handler(CallbackQueryHandler(about_iris_handler, pattern="^about_iris$"))

    # Back to Main Menu handler
    application.add_handler(CallbackQueryHandler(admin_back_to_main_handler, pattern="^student_back_to_main$"))

    # Register fallback callback query handler for student inline keyboard buttons (e.g. CGPA, Search)
    application.add_handler(CallbackQueryHandler(menu_callback_handler))

    # Start polling for incoming messages from Telegram
    print("IRIS bot is starting...")
    application.run_polling()
