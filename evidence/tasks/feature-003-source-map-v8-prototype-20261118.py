"""OFFLINE-only source-rank map prototype; never activated by runtime/worker.

The model would select/rank known sources, while code supplies exact source text.
No silent repair of an invalid v6/v7 response. New profile review/evaluation needed.
"""

from fraudlens.investigation.retrieval_source_map_v8 import decode_selection, source_schema

__all__ = ["decode_selection", "source_schema"]
