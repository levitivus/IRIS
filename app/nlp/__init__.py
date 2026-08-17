"""
app/nlp package initialization.

Exports the isolated NLP processor interface:
- process_query
- NLPResult
- NLPStatus
"""

from app.nlp.processor import NLPResult, NLPStatus, process_query

__all__ = ["process_query", "NLPResult", "NLPStatus"]
