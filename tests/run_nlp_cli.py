"""
tests/run_nlp_cli.py

Optional isolated CLI test utility for manually testing IRIS Phase 8 NLP Query Processor.

Usage:
    python -m tests.run_nlp_cli

CRITICAL CONSTRAINTS:
- Standalone command-line utility for manual developer inspection.
- NO Telegram bot initialization.
- NO PostgreSQL database connection.
- NO modifications to IRIS application or Phase 7 runtime.
"""

import sys
from app.nlp.processor import process_query


def main():
    print("=" * 60)
    print("IRIS Phase 8 NLP Query Processor — Isolated CLI Test Utility")
    print("Type a query string and press Enter. Type 'exit' or 'quit' to stop.")
    print("=" * 60)

    while True:
        try:
            user_input = input("\nQuery > ").strip()
            if user_input.lower() in ["exit", "quit", "q"]:
                print("Exiting NLP CLI runner.")
                break
            if not user_input:
                continue

            result = process_query(user_input)
            print("-" * 40)
            print(f"Status              : {result.status.value}")
            if result.category:
                print(f"Category            : {result.category}")
            if result.subcategory:
                print(f"Subcategory         : {result.subcategory}")
            if result.sub_subcategory:
                print(f"Sub-subcategory     : {result.sub_subcategory}")
            if result.semester:
                print(f"Semester            : {result.semester}")
            if result.subject_code:
                print(f"Subject Code        : {result.subject_code}")
            if result.subject_name:
                print(f"Subject Name        : {result.subject_name}")
            if result.module:
                print(f"Module              : {result.module}")
            if result.year:
                print(f"Year                : {result.year}")
            if result.internal_exam:
                print(f"Internal Exam       : {result.internal_exam}")
            if result.missing_fields:
                print(f"Missing Fields      : {result.missing_fields}")
            if result.ambiguous_field:
                print(f"Ambiguous Field     : {result.ambiguous_field}")
            if result.ambiguous_candidates:
                print(f"Ambiguous Candidates: {result.ambiguous_candidates}")
            if result.reason:
                print(f"Reason              : {result.reason}")
            print("-" * 40)
        except (KeyboardInterrupt, EOFError):
            print("\nExiting NLP CLI runner.")
            break


if __name__ == "__main__":
    main()
