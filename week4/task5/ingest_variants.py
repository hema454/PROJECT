import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "task4"))

from pypdf import PdfReader  # noqa: E402

from chunking_strategies import STRATEGIES  # noqa: E402
from db_variants import init_variant_table, insert_variant_chunk  # noqa: E402
from embeddings import embed_text  # noqa: E402


def load_pdf_pages(path: Path) -> list[tuple[int, str]]:
    reader = PdfReader(str(path))
    return [(i + 1, page.extract_text() or "") for i, page in enumerate(reader.pages)]


def ingest_corpus(corpus_dir: str):
    for table_name in STRATEGIES:
        init_variant_table(table_name)

    for path in Path(corpus_dir).glob("*.pdf"):
        pages = load_pdf_pages(path)
        for table_name, chunk_fn in STRATEGIES.items():
            for page_num, text in pages:
                for chunk in chunk_fn(text):
                    insert_variant_chunk(table_name, path.name, page_num, chunk, embed_text(chunk))
        print(f"ingested {path.name} into all 3 strategies")


if __name__ == "__main__":
    ingest_corpus(sys.argv[1] if len(sys.argv) > 1 else "../task4/corpus")