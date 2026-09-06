"""
Unit tests for the chunking functions, using known input strings with
known expected output -- runs offline, no PDFs or model needed.

Run: python -m unittest tests.test_chunking -v   (from the project root)
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from chunk_fixed import fixed_size_chunks  # noqa: E402
from chunk_recursive import recursive_split  # noqa: E402
from chunk_structure_aware import is_heading, split_into_sections  # noqa: E402


class TestFixedChunking(unittest.TestCase):

    def test_splits_at_exact_size_no_overlap(self):
        text = "a" * 20
        chunks = fixed_size_chunks(text, chunk_size=10, overlap=0)
        self.assertEqual([c for c, _ in chunks], ["a" * 10, "a" * 10])

    def test_overlap_repeats_tail_of_previous_chunk(self):
        text = "0123456789ABCDEFGHIJ"  # 20 chars
        chunks = fixed_size_chunks(text, chunk_size=10, overlap=3)
        texts = [c for c, _ in chunks]
        # second chunk should start with the last 3 chars of the first chunk
        self.assertEqual(texts[0][-3:], texts[1][:3])

    def test_empty_text_gives_no_chunks(self):
        self.assertEqual(fixed_size_chunks("   \n  "), [])


class TestRecursiveChunking(unittest.TestCase):

    def test_short_text_stays_one_chunk(self):
        text = "This is short."
        chunks = recursive_split(text, chunk_size=500, overlap=50)
        self.assertEqual(chunks, [text])

    def test_splits_on_paragraph_boundary_when_possible(self):
        text = ("Paragraph one. " * 5) + "\n\n" + ("Paragraph two. " * 5)
        chunks = recursive_split(text, chunk_size=90, overlap=10)
        self.assertGreater(len(chunks), 1)
        # no chunk should exceed the requested size by more than a small margin
        for c in chunks:
            self.assertLessEqual(len(c), 90 + 10)

    def test_empty_text_gives_no_chunks(self):
        self.assertEqual(recursive_split("   "), [])


class TestStructureAwareChunking(unittest.TestCase):

    def test_numbered_heading_detected(self):
        self.assertTrue(is_heading("4.2 Ingest your corpus three ways"))

    def test_sentence_not_detected_as_heading(self):
        self.assertFalse(is_heading("This is a normal sentence in a paragraph."))

    def test_text_before_first_heading_is_orphaned(self):
        text = "Intro line with no heading above it.\n4.1 First Section\nBody text here."
        sections = split_into_sections(text)
        self.assertEqual(sections[0][0], None)  # orphaned text
        self.assertIn("Intro line", sections[0][1])
        self.assertEqual(sections[1][0], "4.1 First Section")


if __name__ == "__main__":
    unittest.main()