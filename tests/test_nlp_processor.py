"""
tests/test_nlp_processor.py

Isolated unit test suite for the IRIS Phase 8 NLP Query Processor.

Verifies processing of:
- Valid queries (Notes, Question Papers, Projects, Lab Manuals)
- Ambiguous queries and alias collision resolution with/without context
- Incomplete queries (missing required fields)
- Unsupported intent queries
- No-resource conversational queries
- Multiple query requests
- Formatting and casing variations

CRITICAL CONSTRAINTS:
- Standalone execution (no PostgreSQL, no Telegram bot, no network calls).
"""

import unittest
from app.nlp.processor import NLPResult, NLPStatus, process_query


class TestNLPProcessor(unittest.TestCase):

    # ==========================================================================
    # 1. VALID QUERIES
    # ==========================================================================

    def test_valid_notes_query_canonical(self):
        query = "I need third semester DBMS module 2 notes"
        res = process_query(query)
        self.assertEqual(res.status, NLPStatus.VALID)
        self.assertEqual(res.category, "Notes")
        self.assertEqual(res.semester, 3)
        self.assertEqual(res.subject_code, "M24CA1C202")
        self.assertEqual(res.module, 2)

    def test_valid_notes_query_reordered(self):
        query = "DBMS S3 notes module 2"
        res = process_query(query)
        self.assertEqual(res.status, NLPStatus.VALID)
        self.assertEqual(res.category, "Notes")
        self.assertEqual(res.semester, 3)
        self.assertEqual(res.subject_code, "M24CA1C202")
        self.assertEqual(res.module, 2)

    def test_valid_notes_case_variations(self):
        for q in ["s1 ase notes module 1", "S1 ASE NOTES MODULE 1", "Sem-1 Adv Software Eng Mod-1 Notes"]:
            res = process_query(q)
            self.assertEqual(res.status, NLPStatus.VALID, f"Failed for query: {q}")
            self.assertEqual(res.category, "Notes")
            self.assertEqual(res.semester, 1)
            self.assertEqual(res.subject_code, "M24CA1C103")
            self.assertEqual(res.module, 1)

    def test_valid_qp_query(self):
        query = "S3 DAA semester exam question paper 2025"
        res = process_query(query)
        self.assertEqual(res.status, NLPStatus.VALID)
        self.assertEqual(res.category, "Question Papers")
        self.assertEqual(res.subcategory, "Semester Examination")
        self.assertEqual(res.semester, 3)
        self.assertEqual(res.subject_code, "M24CA1C302")
        self.assertEqual(res.year, 2025)

    def test_valid_project_template_query(self):
        query = "Mini Project Project Report Template"
        res = process_query(query)
        self.assertEqual(res.status, NLPStatus.VALID)
        self.assertEqual(res.category, "Projects")
        self.assertEqual(res.subcategory, "Mini Project")
        self.assertEqual(res.sub_subcategory, "Project Report Template")
        # Year should be None for project retrieval parameters
        self.assertIsNone(res.year)

    def test_valid_lab_manual_query(self):
        query = "S1 Web Dev Lab record sample"
        res = process_query(query)
        self.assertEqual(res.status, NLPStatus.VALID)
        self.assertEqual(res.category, "Lab Manuals")
        self.assertEqual(res.subcategory, "Record Samples")
        self.assertEqual(res.semester, 1)
        self.assertEqual(res.subject_code, "M24CA1B105")

    # ==========================================================================
    # 2. AMBIGUOUS QUERIES & CONTEXTUAL DISAMBIGUATION
    # ==========================================================================

    def test_ambiguous_cloud_query_without_context(self):
        query = "cloud notes"
        res = process_query(query)
        self.assertEqual(res.status, NLPStatus.AMBIGUOUS)
        self.assertEqual(res.ambiguous_field, "subject")
        self.assertTrue(len(res.ambiguous_candidates) >= 2)

    def test_contextual_disambiguation_cloud_s2(self):
        query = "S2 cloud notes module 1"
        res = process_query(query)
        self.assertEqual(res.status, NLPStatus.VALID)
        self.assertEqual(res.subject_code, "M24CA1E204D")

    def test_contextual_disambiguation_cloud_s3_aws(self):
        query = "S3 AWS cloud notes module 1"
        res = process_query(query)
        self.assertEqual(res.status, NLPStatus.VALID)
        self.assertEqual(res.subject_code, "M24CA1E304D")

    def test_ambiguous_ds_lab_without_context(self):
        query = "ds lab record sample"
        res = process_query(query)
        self.assertEqual(res.status, NLPStatus.AMBIGUOUS)
        self.assertEqual(res.ambiguous_field, "subject")

    def test_contextual_disambiguation_ds_lab_s1(self):
        query = "S1 DS lab record sample"
        res = process_query(query)
        self.assertEqual(res.status, NLPStatus.VALID)
        self.assertEqual(res.subject_code, "M24CA1L107")

    def test_contextual_disambiguation_ds_lab_s3(self):
        query = "S3 DS lab record sample"
        res = process_query(query)
        self.assertEqual(res.status, NLPStatus.VALID)
        self.assertEqual(res.subject_code, "M24CA1L306")

    def test_ambiguous_data_notes(self):
        query = "data notes"
        res = process_query(query)
        self.assertEqual(res.status, NLPStatus.AMBIGUOUS)
        self.assertEqual(res.ambiguous_field, "subject")

    def test_ambiguous_project_report(self):
        query = "project report template"
        res = process_query(query)
        self.assertEqual(res.status, NLPStatus.AMBIGUOUS)
        self.assertEqual(res.ambiguous_field, "subcategory")

    def test_ambiguous_syllabus(self):
        query = "syllabus"
        res = process_query(query)
        self.assertEqual(res.status, NLPStatus.AMBIGUOUS)

    # ==========================================================================
    # 3. INCOMPLETE QUERIES
    # ==========================================================================

    def test_incomplete_notes_missing_module(self):
        query = "S2 DBMS notes"
        res = process_query(query)
        self.assertEqual(res.status, NLPStatus.INCOMPLETE)
        self.assertIn("module", res.missing_fields)

    def test_incomplete_qp_missing_subcategory(self):
        query = "question paper for ACN"
        res = process_query(query)
        self.assertEqual(res.status, NLPStatus.INCOMPLETE)
        self.assertIn("subcategory", res.missing_fields)

    def test_incomplete_internal_qp_missing_year_and_exam(self):
        query = "S2 internal exam qp for AOS"
        res = process_query(query)
        self.assertEqual(res.status, NLPStatus.INCOMPLETE)
        self.assertTrue("year" in res.missing_fields or "internal_exam" in res.missing_fields)

    # ==========================================================================
    # 4. UNSUPPORTED QUERIES
    # ==========================================================================

    def test_unsupported_summarize(self):
        query = "summarize my DBMS notes"
        res = process_query(query)
        self.assertEqual(res.status, NLPStatus.UNSUPPORTED)

    def test_unsupported_explain(self):
        query = "explain database normalization"
        res = process_query(query)
        self.assertEqual(res.status, NLPStatus.UNSUPPORTED)

    def test_unsupported_solve(self):
        query = "solve this question paper"
        res = process_query(query)
        self.assertEqual(res.status, NLPStatus.UNSUPPORTED)

    def test_unsupported_code_generation(self):
        query = "write a python program for binary search"
        res = process_query(query)
        self.assertEqual(res.status, NLPStatus.UNSUPPORTED)

    def test_unsupported_web_search(self):
        query = "search google for placement interview questions"
        res = process_query(query)
        self.assertEqual(res.status, NLPStatus.UNSUPPORTED)

    # ==========================================================================
    # 5. NO RESOURCE QUERIES
    # ==========================================================================

    def test_no_resource_hello(self):
        query = "hello"
        res = process_query(query)
        self.assertEqual(res.status, NLPStatus.NO_RESOURCE_QUERY)

    def test_no_resource_how_are_you(self):
        query = "how are you?"
        res = process_query(query)
        self.assertEqual(res.status, NLPStatus.NO_RESOURCE_QUERY)

    def test_no_resource_joke(self):
        query = "tell me a joke"
        res = process_query(query)
        self.assertEqual(res.status, NLPStatus.NO_RESOURCE_QUERY)

    def test_no_resource_weather(self):
        query = "what is the weather"
        res = process_query(query)
        self.assertEqual(res.status, NLPStatus.NO_RESOURCE_QUERY)

    def test_no_resource_thanks(self):
        query = "thank you"
        res = process_query(query)
        self.assertEqual(res.status, NLPStatus.NO_RESOURCE_QUERY)

    # ==========================================================================
    # 6. MULTIPLE REQUEST QUERIES
    # ==========================================================================

    def test_multiple_requests_processes_first_only(self):
        query = "S3 DBMS notes and S4 OS question paper"
        res = process_query(query)
        # Should process ONLY "S3 DBMS notes", which is incomplete because module is missing
        self.assertEqual(res.status, NLPStatus.INCOMPLETE)
        self.assertEqual(res.subject_code, "M24CA1C202")
        self.assertIn("module", res.missing_fields)
        # Should NOT contain OS (M24CA1C203)
        self.assertNotEqual(res.subject_code, "M24CA1C203")


if __name__ == "__main__":
    unittest.main()
