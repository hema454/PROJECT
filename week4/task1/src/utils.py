"""
Shared paths and helpers used by every script in src/.

outputs/ is owned here: create_output_dir() is the one function
responsible for creating it. Every script that writes to outputs/
calls this instead of each doing its own os.makedirs().
"""

import os
import numpy as np

HERE = os.path.dirname(__file__)
DATA_DIR = os.path.join(HERE, "..", "data")
OUT_DIR = os.path.join(HERE, "..", "outputs")

CORPUS_PATH = os.path.join(DATA_DIR, "corpus.txt")


def create_output_dir():
    """The single place outputs/ gets created. Call this before writing to it."""
    os.makedirs(OUT_DIR, exist_ok=True)
    return OUT_DIR


def load_corpus_from_data():
    """Read the source corpus directly from data/corpus.txt."""
    with open(CORPUS_PATH, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def load_embedded_corpus():
    """
    Load the embeddings + the exact sentence list they were computed from
    (outputs/sentences.txt), NOT data/corpus.txt directly.

    Why a separate copy in outputs/ instead of re-reading data/corpus.txt:
    outputs/sentences.txt is a frozen snapshot, guaranteed to be in the
    exact same order as outputs/embeddings.npy row-for-row, at the moment
    embed_corpus.py ran. If data/corpus.txt is edited or regenerated later
    (e.g. someone reruns generate_corpus.py with a different sentence
    list) without re-embedding, reading data/corpus.txt here would
    silently misalign sentences[i] with embeddings[i]. Reading the
    outputs/ copy instead makes that impossible -- if it's stale, it's
    obviously stale (wrong content), not silently misaligned.

    allow_pickle=True: the array saved by embed_corpus.py can come back
    from sentence-transformers as an object-dtype array depending on the
    installed version, which numpy's default np.load refuses to load
    without this flag. Safe here since we only ever load a file this
    same pipeline wrote moments earlier -- never an untrusted file.
    """
    embeddings = np.load(os.path.join(OUT_DIR, "embeddings.npy"), allow_pickle=True)
    with open(os.path.join(OUT_DIR, "sentences.txt"), "r", encoding="utf-8") as f:
        sentences = [line.strip() for line in f if line.strip()]
    assert len(sentences) == embeddings.shape[0], (
        f"outputs/sentences.txt has {len(sentences)} lines but "
        f"embeddings.npy has {embeddings.shape[0]} rows -- re-run embed_corpus.py"
    )
    return embeddings, sentences