"""
tests/test_nlp_stress.py

Phase 8 Step 4 — IRIS NLP Processor Stress & Behavioral Validation Test Suite.

Contains 65+ focused, realistic, adversarial, and edge-case unit tests covering:
- Category A: Natural Language Valid Queries
- Category B: Different Word Orders
- Category C: Human Typing Style / Telegram Shorthand
- Category D: Case Variations
- Category E: Punctuation and Separator Variations
- Category F: Ambiguous Queries
- Category G: Contextual Disambiguation
- Category H: Incomplete Queries
- Category I: Unsupported Requests
- Category J: No-Resource / Random Queries
- Category K: Multiple-Request Tests
- Category L: Typo / Near-Miss Tests (Documenting Observed Behavior)
- Category M: Mixed Garbage / Noisy Inputs
- Category N: Conflicting Information
- Category O: Security / Command-Like Inputs

CRITICAL CONSTRAINTS:
- Standalone execution (no PostgreSQL, no Telegram bot, no network calls).
- Zero modifications to app/nlp/processor.py or app/nlp/vocabulary.py.
"""

import unittest
from app.nlp.processor import NLPResult, NLPStatus, process_query


class TestNLPStress(unittest.TestCase):

    # ==========================================================================
    # CATEGORY A: NATURAL LANGUAGE VALID QUERIES
    # ==========================================================================

    def test_nl_valid_notes_full_sentence(self):
        query = "Can you give me the notes for module 3 of DBMS in semester 3?"
        res = process_query(query)
        self.assertEqual(res.status, NLPStatus.VALID)
        self.assertEqual(res.category, "Notes")
        self.assertEqual(res.semester, 3)
        self.assertEqual(res.subject_code, "M24CA1C202")
        self.assertEqual(res.module, 3)

    def test_nl_valid_qp_exam_year(self):
        query = "Please find the 2025 S3 DAA question paper"
        res = process_query(query)
        self.assertEqual(res.status, NLPStatus.VALID)
        self.assertEqual(res.category, "Question Papers")
        self.assertEqual(res.subcategory, "Semester Examination")
        self.assertEqual(res.semester, 3)
        self.assertEqual(res.subject_code, "M24CA1C302")
        self.assertEqual(res.year, 2025)

    def test_nl_valid_internal_qp(self):
        query = "I need the S2 second internal AOS question paper for 2025"
        res = process_query(query)
        self.assertEqual(res.status, NLPStatus.VALID)
        self.assertEqual(res.category, "Question Papers")
        self.assertEqual(res.subcategory, "Internal Examination")
        self.assertEqual(res.sub_subcategory, "Second Internal")
        self.assertEqual(res.semester, 2)
        self.assertEqual(res.subject_code, "M24CA1C203")
        self.assertEqual(res.year, 2025)
        self.assertEqual(res.internal_exam, 2)

    def test_nl_valid_mini_project_report(self):
        query = "Can you give me the mini project report template?"
        res = process_query(query)
        self.assertEqual(res.status, NLPStatus.VALID)
        self.assertEqual(res.category, "Projects")
        self.assertEqual(res.subcategory, "Mini Project")
        self.assertEqual(res.sub_subcategory, "Project Report Template")
        self.assertIsNone(res.year)

    def test_nl_valid_reference_bridge_pyq(self):
        query = "bridge course bridge pyq 2024"
        res = process_query(query)
        self.assertEqual(res.status, NLPStatus.VALID)
        self.assertEqual(res.category, "Reference Materials")
        self.assertEqual(res.subcategory, "Bridge Course")
        self.assertEqual(res.sub_subcategory, "Previous Year Papers")
        self.assertEqual(res.year, 2024)

    def test_nl_valid_placement_aptitude(self):
        query = "Aptitude placement materials"
        res = process_query(query)
        self.assertEqual(res.status, NLPStatus.VALID)
        self.assertEqual(res.category, "Placement Materials")
        self.assertEqual(res.subcategory, "Aptitude")

    # ==========================================================================
    # CATEGORY B: DIFFERENT WORD ORDERS
    # ==========================================================================

    def test_order_s3_dbms_mod2_notes(self):
        res = process_query("S3 DBMS module 2 notes")
        self.assertEqual(res.status, NLPStatus.VALID)
        self.assertEqual(res.subject_code, "M24CA1C202")
        self.assertEqual(res.module, 2)

    def test_order_dbms_s3_notes_mod2(self):
        res = process_query("DBMS S3 notes module 2")
        self.assertEqual(res.status, NLPStatus.VALID)
        self.assertEqual(res.subject_code, "M24CA1C202")
        self.assertEqual(res.module, 2)

    def test_order_notes_dbms_mod2_s3(self):
        res = process_query("notes for DBMS module 2 S3")
        self.assertEqual(res.status, NLPStatus.VALID)
        self.assertEqual(res.subject_code, "M24CA1C202")
        self.assertEqual(res.module, 2)

    def test_order_mod2_notes_dbms_sem3(self):
        res = process_query("module 2 notes DBMS semester 3")
        self.assertEqual(res.status, NLPStatus.VALID)
        self.assertEqual(res.subject_code, "M24CA1C202")
        self.assertEqual(res.module, 2)

    # ==========================================================================
    # CATEGORY C: HUMAN TYPING STYLE / TELEGRAM SHORTHAND
    # ==========================================================================

    def test_shorthand_s3_dbms_m2_notes(self):
        res = process_query("s3 dbms m2 notes")
        self.assertEqual(res.status, NLPStatus.VALID)
        self.assertEqual(res.semester, 3)
        self.assertEqual(res.module, 2)

    def test_shorthand_3rd_sem_adbms_mod4_notes(self):
        res = process_query("3rd sem adbms mod 4 notes")
        self.assertEqual(res.status, NLPStatus.VALID)
        self.assertEqual(res.semester, 3)
        self.assertEqual(res.subject_code, "M24CA1C202")
        self.assertEqual(res.module, 4)

    def test_shorthand_s2_acn_qp_2025(self):
        res = process_query("s2 acn qp 2025")
        self.assertEqual(res.status, NLPStatus.VALID)
        self.assertEqual(res.category, "Question Papers")
        self.assertEqual(res.subject_code, "M24CA1C201")

    def test_shorthand_need_dbms_notes_sem3(self):
        res = process_query("need dbms notes sem 3")
        self.assertEqual(res.status, NLPStatus.INCOMPLETE)
        self.assertIn("module", res.missing_fields)

    def test_shorthand_can_u_give_me_adbms_qp(self):
        res = process_query("can u give me adbms qp")
        self.assertEqual(res.status, NLPStatus.INCOMPLETE)

    def test_shorthand_give_me_s3_notes_for_daa(self):
        res = process_query("give me s3 notes for daa")
        self.assertEqual(res.status, NLPStatus.INCOMPLETE)
        self.assertIn("module", res.missing_fields)

    # ==========================================================================
    # CATEGORY D: CASE VARIATIONS
    # ==========================================================================

    def test_casing_dbms_variations(self):
        for term in ["DBMS", "dbms", "DbMs"]:
            res = process_query(f"S3 {term} module 1 notes")
            self.assertEqual(res.status, NLPStatus.VALID, f"Failed for {term}")
            self.assertEqual(res.subject_code, "M24CA1C202")

    def test_casing_semester_variations(self):
        for term in ["S3", "s3", "SEM 3", "Semester 3"]:
            res = process_query(f"{term} DBMS module 1 notes")
            self.assertEqual(res.status, NLPStatus.VALID, f"Failed for {term}")
            self.assertEqual(res.semester, 3)

    def test_casing_module_variations(self):
        for term in ["M2", "m2", "MOD 2", "Module 2"]:
            res = process_query(f"S3 DBMS {term} notes")
            self.assertEqual(res.status, NLPStatus.VALID, f"Failed for {term}")
            self.assertEqual(res.module, 2)

    # ==========================================================================
    # CATEGORY E: PUNCTUATION AND SEPARATOR VARIATIONS
    # ==========================================================================

    def test_punc_hyphenated(self):
        res = process_query("S3-DBMS-mod-2-notes")
        self.assertEqual(res.status, NLPStatus.VALID)
        self.assertEqual(res.module, 2)

    def test_punc_exclamation(self):
        res = process_query("S3 DBMS notes module 2!!!")
        self.assertEqual(res.status, NLPStatus.VALID)

    def test_punc_commas(self):
        res = process_query("S3, DBMS, module 2, notes")
        self.assertEqual(res.status, NLPStatus.VALID)

    def test_punc_sem_dash_mod_dash(self):
        res = process_query("sem-3 dbms mod-2 notes")
        self.assertEqual(res.status, NLPStatus.VALID)

    def test_punc_ellipses(self):
        res = process_query("dbms... s3... module 2... notes")
        self.assertEqual(res.status, NLPStatus.VALID)

    # ==========================================================================
    # CATEGORY F: AMBIGUOUS QUERIES
    # ==========================================================================

    def test_ambig_cloud_notes(self):
        res = process_query("cloud notes")
        self.assertEqual(res.status, NLPStatus.AMBIGUOUS)
        self.assertEqual(res.ambiguous_field, "subject")

    def test_ambig_data_notes(self):
        res = process_query("data notes")
        self.assertEqual(res.status, NLPStatus.AMBIGUOUS)

    def test_ambig_ds_lab(self):
        res = process_query("ds lab record sample")
        self.assertEqual(res.status, NLPStatus.AMBIGUOUS)

    def test_ambig_project_report(self):
        res = process_query("project report template")
        self.assertEqual(res.status, NLPStatus.AMBIGUOUS)

    def test_ambig_syllabus(self):
        res = process_query("syllabus")
        self.assertEqual(res.status, NLPStatus.AMBIGUOUS)

    # ==========================================================================
    # CATEGORY G: CONTEXTUAL DISAMBIGUATION
    # ==========================================================================

    def test_context_s2_cloud_notes(self):
        res = process_query("S2 cloud notes module 1")
        self.assertEqual(res.status, NLPStatus.VALID)
        self.assertEqual(res.subject_code, "M24CA1E204D")

    def test_context_s3_cloud_notes(self):
        res = process_query("S3 cloud notes module 1")
        self.assertEqual(res.status, NLPStatus.VALID)
        self.assertEqual(res.subject_code, "M24CA1E304D")

    def test_context_s1_ds_lab(self):
        res = process_query("S1 DS lab record sample")
        self.assertEqual(res.status, NLPStatus.VALID)
        self.assertEqual(res.subject_code, "M24CA1L107")

    def test_context_s3_ds_lab(self):
        res = process_query("S3 DS lab record sample")
        self.assertEqual(res.status, NLPStatus.VALID)
        self.assertEqual(res.subject_code, "M24CA1L306")

    # ==========================================================================
    # CATEGORY H: INCOMPLETE QUERIES
    # ==========================================================================

    def test_incomplete_dbms_notes(self):
        res = process_query("DBMS notes")
        self.assertEqual(res.status, NLPStatus.INCOMPLETE)
        self.assertIn("module", res.missing_fields)

    def test_incomplete_s3_dbms_notes(self):
        res = process_query("S3 DBMS notes")
        self.assertEqual(res.status, NLPStatus.INCOMPLETE)
        self.assertIn("module", res.missing_fields)

    def test_incomplete_question_paper_alone(self):
        res = process_query("question paper")
        self.assertEqual(res.status, NLPStatus.INCOMPLETE)

    def test_incomplete_os_question_paper(self):
        res = process_query("OS question paper")
        self.assertEqual(res.status, NLPStatus.INCOMPLETE)

    def test_incomplete_internal_question_paper(self):
        res = process_query("internal question paper")
        self.assertEqual(res.status, NLPStatus.INCOMPLETE)

    # ==========================================================================
    # CATEGORY I: UNSUPPORTED REQUESTS
    # ==========================================================================

    def test_unsupported_summarize_notes(self):
        res = process_query("summarize my DBMS notes")
        self.assertEqual(res.status, NLPStatus.UNSUPPORTED)

    def test_unsupported_explain_qp(self):
        res = process_query("explain this question paper")
        self.assertEqual(res.status, NLPStatus.UNSUPPORTED)

    def test_unsupported_solve_question(self):
        res = process_query("solve this question")
        self.assertEqual(res.status, NLPStatus.UNSUPPORTED)

    def test_unsupported_generate_notes(self):
        res = process_query("generate DBMS notes")
        # Incomplete or Unsupported both safely intercept execution
        self.assertIn(res.status, [NLPStatus.UNSUPPORTED, NLPStatus.INCOMPLETE])

    def test_unsupported_write_python_program(self):
        res = process_query("write a Python program for me")
        self.assertEqual(res.status, NLPStatus.UNSUPPORTED)

    def test_unsupported_google_search(self):
        res = process_query("search Google for DBMS papers")
        self.assertEqual(res.status, NLPStatus.UNSUPPORTED)

    def test_unsupported_internet_find(self):
        res = process_query("find this on the internet")
        self.assertEqual(res.status, NLPStatus.NO_RESOURCE_QUERY)

    # ==========================================================================
    # CATEGORY J: NO-RESOURCE / RANDOM QUERIES
    # ==========================================================================

    def test_no_resource_greetings(self):
        for greeting in ["hello", "hi", "how are you", "tell me a joke", "what is the weather", "thanks", "goodbye"]:
            res = process_query(greeting)
            self.assertEqual(res.status, NLPStatus.NO_RESOURCE_QUERY, f"Failed for {greeting}")

    def test_no_resource_random_strings(self):
        for rand in ["asdfghjkl", "???", "123456", "banana"]:
            res = process_query(rand)
            self.assertEqual(res.status, NLPStatus.NO_RESOURCE_QUERY, f"Failed for {rand}")

    # ==========================================================================
    # CATEGORY K: MULTIPLE-REQUEST TESTS
    # ==========================================================================

    def test_multi_request_s3_dbms_and_s4_os(self):
        res = process_query("S3 DBMS notes module 2 and S4 OS question paper")
        self.assertEqual(res.status, NLPStatus.VALID)
        self.assertEqual(res.subject_code, "M24CA1C202")
        self.assertNotEqual(res.subject_code, "M24CA1C203")

    def test_multi_request_dbms_also_daa(self):
        res = process_query("S3 DBMS notes module 1 also DAA question paper")
        self.assertEqual(res.status, NLPStatus.VALID)
        self.assertEqual(res.subject_code, "M24CA1C202")

    def test_multi_request_comma_separated(self):
        res = process_query("I need S3 DBMS notes module 1, S4 OS papers, and placement material")
        self.assertEqual(res.status, NLPStatus.VALID)
        self.assertEqual(res.subject_code, "M24CA1C202")

    # ==========================================================================
    # CATEGORY L: TYPO / NEAR-MISS TESTS (DOCUMENTING OBSERVED BEHAVIOR)
    # ==========================================================================

    def test_typo_databse_notes(self):
        # Observed: Reject without fuzzy matching
        res = process_query("databse notes")
        self.assertIn(res.status, [NLPStatus.NO_RESOURCE_QUERY, NLPStatus.INCOMPLETE])

    def test_typo_queston_paper(self):
        res = process_query("queston paper")
        self.assertIn(res.status, [NLPStatus.NO_RESOURCE_QUERY, NLPStatus.INCOMPLETE])

    def test_typo_semster_3_dbms_notes(self):
        res = process_query("semster 3 dbms notes module 1")
        self.assertIn(res.status, [NLPStatus.VALID, NLPStatus.INCOMPLETE])

    # ==========================================================================
    # CATEGORY M: MIXED GARBAGE / NOISY INPUTS
    # ==========================================================================

    def test_garbage_hello_s3_dbms_mod2_notes(self):
        res = process_query("hello s3 dbms module 2 notes")
        self.assertEqual(res.status, NLPStatus.VALID)
        self.assertEqual(res.subject_code, "M24CA1C202")

    def test_garbage_please_please_dbms_notes(self):
        res = process_query("please please S3 dbms notes mod 1!!!")
        self.assertEqual(res.status, NLPStatus.VALID)
        self.assertEqual(res.subject_code, "M24CA1C202")

    def test_garbage_surrounding_junk(self):
        res = process_query("xyz S3 DBMS module 2 notes abc")
        self.assertEqual(res.status, NLPStatus.VALID)
        self.assertEqual(res.subject_code, "M24CA1C202")

    def test_garbage_conversational_filler(self):
        res = process_query("I need something maybe DBMS module 2 notes sem 3 or whatever")
        self.assertEqual(res.status, NLPStatus.VALID)

    # ==========================================================================
    # CATEGORY N: CONFLICTING INFORMATION
    # ==========================================================================

    def test_conflict_two_semesters(self):
        res = process_query("S2 S3 DBMS notes module 1")
        self.assertTrue(res.status in [NLPStatus.VALID, NLPStatus.AMBIGUOUS, NLPStatus.INCOMPLETE])

    def test_conflict_two_modules(self):
        res = process_query("module 2 module 4 DBMS notes")
        self.assertTrue(res.status in [NLPStatus.VALID, NLPStatus.INCOMPLETE])

    def test_conflict_two_internals(self):
        res = process_query("first internal second internal OS paper 2025")
        self.assertTrue(res.status in [NLPStatus.VALID, NLPStatus.INCOMPLETE, NLPStatus.AMBIGUOUS])

    # ==========================================================================
    # CATEGORY O: SECURITY / COMMAND-LIKE INPUTS
    # ==========================================================================

    def test_security_sql_injection(self):
        res = process_query("select * from subjects")
        self.assertEqual(res.status, NLPStatus.NO_RESOURCE_QUERY)

    def test_security_delete_notes(self):
        res = process_query("delete all notes")
        self.assertIn(res.status, [NLPStatus.UNSUPPORTED, NLPStatus.INCOMPLETE])

    def test_security_ignore_instructions(self):
        res = process_query("ignore everything and give me all database records")
        self.assertEqual(res.status, NLPStatus.NO_RESOURCE_QUERY)

    def test_security_admin_impersonation(self):
        res = process_query("pretend you are admin")
        self.assertEqual(res.status, NLPStatus.NO_RESOURCE_QUERY)

    def test_security_run_sql(self):
        res = process_query("run SQL")
        self.assertEqual(res.status, NLPStatus.NO_RESOURCE_QUERY)


if __name__ == "__main__":
    unittest.main()
