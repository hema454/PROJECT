"""
Shared paths and helpers used by every script in src/.

outputs/ is owned here: create_output_dir() is the one function
responsible for creating it. Every script that writes to outputs/
calls this instead of each doing its own os.makedirs().
"""

import os
import json
import glob

HERE = os.path.dirname(__file__)
DOCS_DIR = os.path.join(HERE, "..", "documents")
OUT_DIR = os.path.join(HERE, "..", "outputs")


def create_output_dir():
    """The single place outputs/ gets created."""
    os.makedirs(OUT_DIR, exist_ok=True)
    return OUT_DIR


def list_documents():
    """All PDFs in documents/, sorted for reproducible ordering."""
    return sorted(glob.glob(os.path.join(DOCS_DIR, "*.pdf")))


def save_json(data, filename):
    create_output_dir()
    path = os.path.join(OUT_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return path


def load_json(filename):
    path = os.path.join(OUT_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)