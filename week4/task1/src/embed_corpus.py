"""
Step 1 (concepts 4.1-4.3): Embed all 200 sentences in the corpus.

Uses sentence-transformers' all-MiniLM-L6-v2 (384 dimensions) — small,
fast, and a common real-world default for exactly this kind of exercise.

Run: python src/embed_corpus.py
Requires internet access the first time (downloads the model from
Hugging Face, ~90MB, then it is cached locally for future runs).

Output:
  outputs/embeddings.npy  -> numpy array, shape (200, 384)
  outputs/sentences.txt   -> copy of the corpus, same order as embeddings.npy
"""

import os
import numpy as np
from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"

HERE = os.path.dirname(__file__)
CORPUS_PATH = os.path.join(HERE, "..", "data", "corpus.txt")
OUT_DIR = os.path.join(HERE, "..", "outputs")


def load_corpus(path):
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    sentences = load_corpus(CORPUS_PATH)
    print(f"Loaded {len(sentences)} sentences from {CORPUS_PATH}")

    print(f"Loading model: {MODEL_NAME} ...")
    model = SentenceTransformer(MODEL_NAME)

    print("Embedding sentences...")
    embeddings = model.encode(
        sentences,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=False,  # keep raw vectors; we normalize explicitly later
    )

    print(f"Embeddings shape: {embeddings.shape}")  # (200, 384)

    np.save(os.path.join(OUT_DIR, "embeddings.npy"), embeddings)
    with open(os.path.join(OUT_DIR, "sentences.txt"), "w", encoding="utf-8") as f:
        for s in sentences:
            f.write(s + "\n")

    print(f"Saved embeddings to {OUT_DIR}/embeddings.npy")
    print(f"Saved sentence index to {OUT_DIR}/sentences.txt")


if __name__ == "__main__":
    main()