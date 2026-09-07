"""
Unit tests for the manual cosine similarity implementation in
nearest_neighbors.py, using known input vectors and known expected scores
-- not dependent on the embedding model or the corpus, so it runs fast
and offline.

Run: python -m unittest tests/test_cosine_similarity.py -v
  (from the project root, e.g. semantic-similarity-exercise/)
"""

import os
import sys
import unittest
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from nearest_neighbors import cosine_similarity_manual  # noqa: E402


class TestCosineSimilarityManual(unittest.TestCase):

    def test_identical_vectors_give_similarity_1(self):
        query = np.array([1.0, 0.0, 0.0])
        corpus = np.array([[1.0, 0.0, 0.0]])
        result = cosine_similarity_manual(query, corpus)
        np.testing.assert_allclose(result, [1.0], atol=1e-6)

    def test_orthogonal_vectors_give_similarity_0(self):
        query = np.array([1.0, 0.0])
        corpus = np.array([[0.0, 1.0]])
        result = cosine_similarity_manual(query, corpus)
        np.testing.assert_allclose(result, [0.0], atol=1e-6)

    def test_opposite_vectors_give_similarity_minus_1(self):
        query = np.array([1.0, 0.0])
        corpus = np.array([[-1.0, 0.0]])
        result = cosine_similarity_manual(query, corpus)
        np.testing.assert_allclose(result, [-1.0], atol=1e-6)

    def test_scale_invariance(self):
        # cosine similarity should not change if a vector is scaled --
        # only its direction matters, not its magnitude.
        query = np.array([1.0, 1.0])
        corpus = np.array([[2.0, 2.0], [20.0, 20.0]])  # same direction, different scale
        result = cosine_similarity_manual(query, corpus)
        np.testing.assert_allclose(result, [1.0, 1.0], atol=1e-6)

    def test_known_45_degree_angle(self):
        # cos(45 deg) = 1/sqrt(2) ~= 0.7071
        query = np.array([1.0, 0.0])
        corpus = np.array([[1.0, 1.0]])
        result = cosine_similarity_manual(query, corpus)
        np.testing.assert_allclose(result, [0.70710678], atol=1e-6)

    def test_multiple_corpus_rows_at_once(self):
        query = np.array([1.0, 0.0])
        corpus = np.array([
            [1.0, 0.0],   # identical -> 1.0
            [0.0, 1.0],   # orthogonal -> 0.0
            [-1.0, 0.0],  # opposite -> -1.0
        ])
        result = cosine_similarity_manual(query, corpus)
        np.testing.assert_allclose(result, [1.0, 0.0, -1.0], atol=1e-6)


if __name__ == "__main__":
    unittest.main()