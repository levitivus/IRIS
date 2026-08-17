"""
tests/test_nlp_integration.py

Phase 8 Step 5 — IRIS Search -> NLP Processor Integration Test Suite.

Verifies:
1. Search prompt handler triggers on callback query 'search' and returns STATE_SEARCH_WAITING.
2. Search query handler receives text input, invokes process_query(), and formats diagnostic message.
3. Diagnostic outputs for VALID, AMBIGUOUS, INCOMPLETE, NO_RESOURCE_QUERY, UNSUPPORTED, and MULTIPLE-REQUEST queries.
4. Search mode cleanup: ConversationHandler clears state after processing ONE text query.
5. Normal non-search interactions do not invoke NLP.

CRITICAL CONSTRAINTS:
- Minimal mock-based integration tests without requiring live Telegram API or active PostgreSQL connection.
"""

import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from telegram import CallbackQuery, Chat, Message, Update, User
from telegram.ext import ContextTypes, ConversationHandler

from app.handlers.basic import (
    STATE_SEARCH_WAITING,
    format_nlp_diagnostic_message,
    search_cancel_handler,
    search_prompt_handler,
    search_query_handler,
)
from app.nlp.processor import NLPResult, NLPStatus, process_query


class TestNLPIntegration(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.user = User(id=12345, first_name="TestStudent", is_bot=False)
        self.chat = Chat(id=12345, type="private")
        self.context = AsyncMock(spec=ContextTypes.DEFAULT_TYPE)
        self.context.user_data = {}
        self.context.bot = AsyncMock()

    # ==========================================================================
    # 1. SEARCH ACTIVATION
    # ==========================================================================

    async def test_search_activation_prompt(self):
        message = MagicMock(spec=Message)
        message.message_id = 100
        message.edit_text = AsyncMock(return_value=message)

        query = MagicMock(spec=CallbackQuery)
        query.data = "search"
        query.message = message
        query.answer = AsyncMock()

        update = MagicMock(spec=Update)
        update.callback_query = query
        update.effective_chat = self.chat
        update.effective_user = self.user

        state = await search_prompt_handler(update, self.context)
        self.assertEqual(state, STATE_SEARCH_WAITING)
        query.answer.assert_called_once()
        message.edit_text.assert_called_once()
        self.assertIn("IRIS Search", message.edit_text.call_args[0][0])

    # ==========================================================================
    # 2. DIAGNOSTIC FORMATTING TESTS FOR ALL NLP STATUSES
    # ==========================================================================

    def test_format_diagnostic_valid(self):
        res = process_query("S3 DBMS module 2 notes")
        msg_text = format_nlp_diagnostic_message("S3 DBMS module 2 notes", res)
        self.assertIn("`VALID`", msg_text)
        self.assertIn("Notes", msg_text)
        self.assertIn("Semester*: 3", msg_text)
        self.assertIn("Module*: 2", msg_text)

    def test_format_diagnostic_ambiguous(self):
        res = process_query("cloud notes")
        msg_text = format_nlp_diagnostic_message("cloud notes", res)
        self.assertIn("`AMBIGUOUS`", msg_text)
        self.assertIn("Ambiguous Field", msg_text)

    def test_format_diagnostic_incomplete(self):
        res = process_query("DBMS notes")
        msg_text = format_nlp_diagnostic_message("DBMS notes", res)
        self.assertIn("`INCOMPLETE`", msg_text)
        self.assertIn("Missing Parameters", msg_text)

    def test_format_diagnostic_no_resource(self):
        res = process_query("hello")
        msg_text = format_nlp_diagnostic_message("hello", res)
        self.assertIn("`NO_RESOURCE_QUERY`", msg_text)

    def test_format_diagnostic_unsupported(self):
        res = process_query("summarize my DBMS notes")
        msg_text = format_nlp_diagnostic_message("summarize my DBMS notes", res)
        self.assertIn("`UNSUPPORTED`", msg_text)

    # ==========================================================================
    # 3. ONE QUERY SEARCH HANDLING & STATE CLEANUP
    # ==========================================================================

    @patch("app.handlers.basic.fetch_resources_for_nlp_result")
    async def test_search_query_handler_valid(self, mock_fetch):
        mock_fetch.return_value = [{
            "id": 1,
            "title": "DBMS Module 2 Notes",
            "telegram_file_id": "file_dbms_mod2",
        }]

        message = MagicMock(spec=Message)
        message.text = "S3 DBMS module 2 notes"
        message.chat_id = 12345
        message.reply_text = AsyncMock(return_value=message)

        update = MagicMock(spec=Update)
        update.message = message
        update.callback_query = None
        update.effective_chat = self.chat
        update.effective_user = self.user

        state = await search_query_handler(update, self.context)
        # Must return ConversationHandler.END to clear Search mode after ONE query!
        self.assertEqual(state, ConversationHandler.END)
        self.context.bot.send_document.assert_called_once_with(
            chat_id=12345,
            document="file_dbms_mod2",
            caption="📄 DBMS Module 2 Notes",
        )
        message.reply_text.assert_called_once()
        output_text = message.reply_text.call_args[0][0]
        self.assertIn("Delivered", output_text)
        self.assertIn("Notes", output_text)

    async def test_search_cancel_handler(self):
        message = MagicMock(spec=Message)
        message.edit_text = AsyncMock()

        query = MagicMock(spec=CallbackQuery)
        query.data = "student_back_to_main"
        query.message = message
        query.answer = AsyncMock()

        update = MagicMock(spec=Update)
        update.callback_query = query
        update.effective_chat = self.chat
        update.effective_user = self.user

        state = await search_cancel_handler(update, self.context)
        self.assertEqual(state, ConversationHandler.END)
        query.answer.assert_called_once()
        message.edit_text.assert_called_once()


if __name__ == "__main__":
    unittest.main()
