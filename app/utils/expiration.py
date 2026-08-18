"""
app/utils/expiration.py

Module for managing temporary bot UI message expiration and per-chat inactivity timers in IRIS.
Automatically deletes tracked bot navigation/UI messages after 10 minutes of inactivity,
while strictly preserving user messages, delivered academic PDFs/documents, and normal chat history.
"""

from typing import Dict, Optional, Set
from telegram import Message, Update
from telegram.ext import ContextTypes

# In-memory mapping: chat_id (int) -> Set of tracked temporary UI message_ids (Set[int])
_temporary_ui_messages: Dict[int, Set[int]] = {}

# Inactivity timeout constant: 10 minutes = 600 seconds
INACTIVITY_TIMEOUT_SECONDS = 600


def track_temp_message(chat_id: int, message_id: int) -> None:
    """
    Registers a bot-generated temporary UI/navigation message ID for cleanup.
    """
    if chat_id not in _temporary_ui_messages:
        _temporary_ui_messages[chat_id] = set()
    _temporary_ui_messages[chat_id].add(message_id)


async def cleanup_tracked_ui_messages(bot, chat_id: int) -> None:
    """
    Deletes all currently tracked temporary bot UI/navigation messages for a chat.
    Invoked upon successful resource delivery so that obsolete navigation UI
    above the delivered file is removed, allowing the next-action menu to appear
    directly below the delivered file.
    Does NOT delete user messages or delivered PDF files.
    """
    msg_ids = _temporary_ui_messages.pop(chat_id, set())
    for msg_id in msg_ids:
        try:
            await bot.delete_message(chat_id=chat_id, message_id=msg_id)
        except Exception:
            pass


def reset_inactivity_timer(context: ContextTypes.DEFAULT_TYPE, chat_id: int, timeout_seconds: int = INACTIVITY_TIMEOUT_SECONDS) -> None:
    """
    Resets the 10-minute inactivity cleanup timer for a given chat_id.
    Cancels any existing pending cleanup job for this chat and schedules a new one.
    """
    if not context.job_queue:
        return

    job_name = f"cleanup_{chat_id}"

    # Remove any existing pending cleanup job for this chat
    existing_jobs = context.job_queue.get_jobs_by_name(job_name)
    for job in existing_jobs:
        job.schedule_removal()

    # Schedule a new one-shot cleanup job for +timeout_seconds
    context.job_queue.run_once(
        _cleanup_inactive_chat_job,
        when=timeout_seconds,
        chat_id=chat_id,
        name=job_name,
        data={"chat_id": chat_id},
    )


async def _cleanup_inactive_chat_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Job callback function executed after 10 minutes of inactivity.
    Deletes all tracked temporary bot UI messages for the chat and clears session state.
    """
    job = context.job
    if not job:
        return

    chat_id = job.chat_id or (job.data.get("chat_id") if job.data else None)
    if not chat_id:
        return

    # Pop tracked temporary UI message IDs for this chat
    msg_ids = _temporary_ui_messages.pop(chat_id, set())

    # Delete each tracked temporary UI message
    for msg_id in msg_ids:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=msg_id)
        except Exception:
            # Graceful error handling (e.g. message already deleted or expired)
            pass

    # Clear temporary user session state (e.g. active CGPA or upload wizard sessions)
    try:
        if context.application and context.application.user_data:
            user_data_dict = context.application.user_data.get(chat_id, {})
            if isinstance(user_data_dict, dict):
                user_data_dict.pop("cgpa", None)
                user_data_dict.pop("upload", None)
    except Exception:
        pass


def register_activity_and_track(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    bot_message: Optional[Message] = None,
) -> None:
    """
    Convenience helper function to register chat activity (resets 10-min timer)
    and optionally track a bot-generated temporary UI message.
    """
    chat_id = None
    if update.effective_chat:
        chat_id = update.effective_chat.id

    if chat_id:
        reset_inactivity_timer(context, chat_id)
        if bot_message and bot_message.message_id:
            track_temp_message(chat_id, bot_message.message_id)
        elif update.callback_query and update.callback_query.message:
            track_temp_message(chat_id, update.callback_query.message.message_id)


async def global_activity_tracker_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Global TypeHandler callback that fires on every update to reset the 10-minute
    inactivity timer for the active chat and track button-clicked UI message IDs.
    """
    if update.effective_chat:
        chat_id = update.effective_chat.id
        reset_inactivity_timer(context, chat_id)
        if update.callback_query and update.callback_query.message:
            track_temp_message(chat_id, update.callback_query.message.message_id)
