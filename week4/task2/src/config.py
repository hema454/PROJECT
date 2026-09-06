"""
Single source of truth for this task's parameters. Every script imports
from here instead of hardcoding values -- same pattern as task1's config.py.
"""

# Chunking parameters (4.6, 4.7)
CHUNK_SIZE = 500       # characters per chunk (fixed + recursive)
CHUNK_OVERLAP = 75     # characters of overlap between consecutive chunks

# Structure-aware chunking: if a section under a heading is still bigger
# than this many characters, it gets sub-split using the same recursive
# logic as chunk_recursive.py, instead of becoming one giant chunk.
STRUCTURE_MAX_SECTION_SIZE = 800

# Heading detection heuristics (used by chunk_structure_aware.py) -- a
# line counts as a heading if it matches ANY of these patterns.
import re  # noqa: E402

HEADING_PATTERNS = [
    re.compile(r"^\d+(\.\d+)*\s+[A-Z].{0,80}$"),   # "4.2 Ingest your corpus"
    re.compile(r"^[A-Z][A-Za-z0-9 /&\-]{2,70}$"),  # short Title Case / ALL CAPS line, no trailing punctuation
]
MIN_HEADING_LEN = 3
MAX_HEADING_LEN = 80