import re

from config import settings
from models import Citation


def extract_citations(answer: str, chunks: list[dict]) -> list[Citation]:
    used = {int(n) for n in re.findall(r"\[(\d+)\]", answer)}
    citations = []
    seen = set()
    for i, c in enumerate(chunks, start=1):
        if i in used and (c["doc_name"], c["page"]) not in seen:
            seen.add((c["doc_name"], c["page"]))
            citations.append(
                Citation(
                    doc_name=c["doc_name"],
                    page=c["page"],
                    url=f"{settings.doc_link_base}{c['doc_name']}#page={c['page']}",
                )
            )
    return citations