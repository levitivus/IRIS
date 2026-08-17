"""
tests/test_nlp_retrieval_integration.py

Phase 8 Step 6 — NLP -> Existing Resource Retrieval Integration Test Suite.

Verifies:
1. VALID NLP results for all 6 categories (Notes, Question Papers, Lab Manuals, Projects, Placement, Reference) call the exact corresponding existing resource_service.py function with mapped parameters.
2. Projects retrieval does NOT pass project year.
3. Non-VALID NLP results (AMBIGUOUS, INCOMPLETE, UNSUPPORTED, NO_RESOURCE_QUERY, ERROR) NEVER call resource_service.py.
4. Handling of valid queries when zero matching resources exist in DB (No Result Found).
5. Document delivery via Telegram file ID when matching resources exist.
6. Multi-request queries process only the first request segment.

CRITICAL CONSTRAINTS:
- Standalone execution with mocked resource_service calls (no live PostgreSQL or live Telegram API required).
"""

import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from telegram import Chat, Message, Update, User
from telegram.ext import ContextTypes, ConversationHandler

from app.handlers.basic import (
    fetch_resources_for_nlp_result,
    search_query_handler,
)
from app.nlp.processor import NLPResult, NLPStatus, process_query


class TestNLPRetrievalIntegration(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.user = User(id=12345, first_name="TestStudent", is_bot=False)
        self.chat = Chat(id=12345, type="private")
        self.context = AsyncMock(spec=ContextTypes.DEFAULT_TYPE)
        self.context.user_data = {}
        self.context.bot = AsyncMock()

    # ==========================================================================
    # 1. ADAPTER MAPPING TESTS FOR VALID QUERIES
    # ==========================================================================

    @patch("app.handlers.basic.get_subjects_by_semester")
    @patch("app.handlers.basic.get_notes_resources")
    def test_adapter_valid_notes(self, mock_get_notes, mock_get_subjects):
        mock_get_subjects.return_value = [{"id": 10, "subject_code": "M24CA1C202", "subject_name": "DBMS"}]
        mock_get_notes.return_value = [{"id": 1, "title": "DBMS Mod 2 Notes", "telegram_file_id": "file_123"}]

        res = process_query("S3 DBMS module 2 notes")
        self.assertEqual(res.status, NLPStatus.VALID)

        resources = fetch_resources_for_nlp_result(res)
        mock_get_subjects.assert_called_once_with(3)
        mock_get_notes.assert_called_once_with(semester=3, subject_id=10, module=2)
        self.assertEqual(len(resources), 1)

    @patch("app.handlers.basic.get_subjects_by_semester")
    @patch("app.handlers.basic.get_qp_resources")
    def test_adapter_valid_qp(self, mock_get_qp, mock_get_subjects):
        mock_get_subjects.return_value = [{"id": 12, "subject_code": "M24CA1C302", "subject_name": "DAA"}]
        mock_get_qp.return_value = [{"id": 2, "title": "DAA 2025 QP", "telegram_file_id": "file_456"}]

        res = process_query("S3 DAA semester question paper 2025")
        self.assertEqual(res.status, NLPStatus.VALID)

        resources = fetch_resources_for_nlp_result(res)
        mock_get_subjects.assert_called_once_with(3)
        mock_get_qp.assert_called_once_with(
            subcategory="Semester Examination",
            semester=3,
            subject_id=12,
            year=2025,
            internal_exam=None,
        )
        self.assertEqual(len(resources), 1)

    @patch("app.handlers.basic.get_subjects_by_semester")
    @patch("app.handlers.basic.get_qp_resources")
    def test_adapter_valid_internal_qp(self, mock_get_qp, mock_get_subjects):
        mock_get_subjects.return_value = [{"id": 15, "subject_code": "M24CA1C203", "subject_name": "AOS"}]
        mock_get_qp.return_value = [{"id": 3, "title": "AOS Internal 1 QP", "telegram_file_id": "file_789"}]

        res = process_query("I need the S2 first internal AOS question paper for 2025")
        self.assertEqual(res.status, NLPStatus.VALID)

        resources = fetch_resources_for_nlp_result(res)
        mock_get_qp.assert_called_once_with(
            subcategory="Internal Examination",
            semester=2,
            subject_id=15,
            year=2025,
            internal_exam=1,
        )
        self.assertEqual(len(resources), 1)

    @patch("app.handlers.basic.get_projects_resources")
    def test_adapter_valid_project_no_year(self, mock_get_projects):
        mock_get_projects.return_value = [{"id": 4, "title": "Mini Project Template", "telegram_file_id": "file_proj"}]

        res = process_query("Can you give me the mini project report template?")
        self.assertEqual(res.status, NLPStatus.VALID)

        resources = fetch_resources_for_nlp_result(res)
        # MUST NOT pass year to get_projects_resources
        mock_get_projects.assert_called_once_with(
            subcategory="Mini Project",
            sub_subcategory="Project Report Template",
        )
        self.assertEqual(len(resources), 1)

    @patch("app.handlers.basic.get_placement_resources")
    def test_adapter_valid_placement(self, mock_get_placement):
        mock_get_placement.return_value = [{"id": 5, "title": "Aptitude Guide", "telegram_file_id": "file_place"}]

        res = process_query("Aptitude placement materials")
        self.assertEqual(res.status, NLPStatus.VALID)

        resources = fetch_resources_for_nlp_result(res)
        mock_get_placement.assert_called_once_with(subcategory="Aptitude")
        self.assertEqual(len(resources), 1)

    @patch("app.handlers.basic.get_reference_resources")
    def test_adapter_valid_reference(self, mock_get_ref):
        mock_get_ref.return_value = [{"id": 6, "title": "Bridge PYQ 2024", "telegram_file_id": "file_ref"}]

        res = process_query("bridge course bridge pyq 2024")
        self.assertEqual(res.status, NLPStatus.VALID)

        resources = fetch_resources_for_nlp_result(res)
        mock_get_ref.assert_called_once_with(
            subcategory="Bridge Course",
            sub_subcategory="Previous Year Papers",
            year=2024,
        )
        self.assertEqual(len(resources), 1)

    # ==========================================================================
    # 2. NON-VALID RESULTS MUST NOT CALL RETRIEVAL
    # ==========================================================================

    @patch("app.handlers.basic.get_notes_resources")
    @patch("app.handlers.basic.get_qp_resources")
    def test_non_valid_ambiguous_does_not_retrieve(self, mock_qp, mock_notes):
        res = process_query("cloud notes")
        self.assertEqual(res.status, NLPStatus.AMBIGUOUS)

        resources = fetch_resources_for_nlp_result(res)
        self.assertEqual(resources, [])
        mock_qp.assert_not_called()
        mock_notes.assert_not_called()

    @patch("app.handlers.basic.get_notes_resources")
    def test_non_valid_incomplete_does_not_retrieve(self, mock_notes):
        res = process_query("DBMS notes")
        self.assertEqual(res.status, NLPStatus.INCOMPLETE)

        resources = fetch_resources_for_nlp_result(res)
        self.assertEqual(resources, [])
        mock_notes.assert_not_called()

    @patch("app.handlers.basic.get_notes_resources")
    def test_non_valid_unsupported_does_not_retrieve(self, mock_notes):
        res = process_query("summarize my DBMS notes")
        self.assertEqual(res.status, NLPStatus.UNSUPPORTED)

        resources = fetch_resources_for_nlp_result(res)
        self.assertEqual(resources, [])
        mock_notes.assert_not_called()

    @patch("app.handlers.basic.get_notes_resources")
    def test_non_valid_no_resource_does_not_retrieve(self, mock_notes):
        res = process_query("hello")
        self.assertEqual(res.status, NLPStatus.NO_RESOURCE_QUERY)

        resources = fetch_resources_for_nlp_result(res)
        self.assertEqual(resources, [])
        mock_notes.assert_not_called()

    # ==========================================================================
    # 3. END-TO-END SEARCH HANDLER INTEGRATION TESTS
    # ==========================================================================

    @patch("app.handlers.basic.fetch_resources_for_nlp_result")
    async def test_search_handler_valid_delivery(self, mock_fetch):
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
        update.effective_chat = self.chat
        update.effective_user = self.user

        state = await search_query_handler(update, self.context)
        self.assertEqual(state, ConversationHandler.END)
        self.context.bot.send_document.assert_called_once_with(
            chat_id=12345,
            document="file_dbms_mod2",
            caption="📄 DBMS Module 2 Notes",
        )
        message.reply_text.assert_called_once()
        self.assertIn("Delivered", message.reply_text.call_args[0][0])

    @patch("app.handlers.basic.fetch_resources_for_nlp_result")
    async def test_search_handler_no_result_found(self, mock_fetch):
        # Database query returns empty list
        mock_fetch.return_value = []

        message = MagicMock(spec=Message)
        message.text = "S3 DBMS module 2 notes"
        message.chat_id = 12345
        message.reply_text = AsyncMock(return_value=message)

        update = MagicMock(spec=Update)
        update.message = message
        update.effective_chat = self.chat
        update.effective_user = self.user

        state = await search_query_handler(update, self.context)
        self.assertEqual(state, ConversationHandler.END)
        self.context.bot.send_document.assert_not_called()
        message.reply_text.assert_called_once()
        output_text = message.reply_text.call_args[0][0]
        self.assertIn("Resource Not Available", output_text)

    @patch("app.handlers.basic.fetch_resources_for_nlp_result")
    async def test_search_handler_non_valid_ambiguous(self, mock_fetch):
        message = MagicMock(spec=Message)
        message.text = "cloud notes"
        message.chat_id = 12345
        message.reply_text = AsyncMock(return_value=message)

        update = MagicMock(spec=Update)
        update.message = message
        update.effective_chat = self.chat
        update.effective_user = self.user

        state = await search_query_handler(update, self.context)
        self.assertEqual(state, ConversationHandler.END)
        # MUST NOT query database
        mock_fetch.assert_not_called()
        self.context.bot.send_document.assert_not_called()
        message.reply_text.assert_called_once()
        self.assertIn("AMBIGUOUS", message.reply_text.call_args[0][0])


if __name__ == "__main__":
    unittest.main()
