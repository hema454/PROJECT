"""
Step 1 (concepts 4.9, 4.11): Load your assigned documents.

For each PDF in documents/:
  - Extract text per page using pypdf.
  - If a page's extracted text is empty/whitespace-only, that page is
    treated as a scanned image with no text layer (4.11's "OCR" case).
    We fall back to OCR (pytesseract + pdf2image) to recover text.
  - If OCR itself is unavailable (missing tesseract/poppler binaries)
    or fails, the page is recorded with ocr_attempted=True,
    ocr_succeeded=False, and empty text -- NOT silently dropped. The
    gap is visible in the output, not hidden.

Run: python src/load_documents.py
Output: outputs/loaded_documents.json
  -> list of pages: {source, page_number, text, ocr_used, ocr_succeeded}
"""

import os
import sys
from datetime import date

from pypdf import PdfReader

from utils import create_output_dir, list_documents, save_json

# OCR dependencies are optional -- imported lazily so this script still
# runs (and handles normal, non-scanned PDFs) even if they're missing.
try:
    import pytesseract
    from pdf2image import convert_from_path
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False


def extract_text_pages(pdf_path):
    """Returns a list of raw extracted text strings, one per page."""
    reader = PdfReader(pdf_path)
    return [page.extract_text() or "" for page in reader.pages]


def ocr_page(pdf_path, page_index):
    """
    Run OCR on a single page of a PDF by rendering it to an image first.
    page_index is 0-based; pdf2image's first_page/last_page are 1-based.
    """
    images = convert_from_path(
        pdf_path, first_page=page_index + 1, last_page=page_index + 1
    )
    if not images:
        return ""
    return pytesseract.image_to_string(images[0])


def load_pdf(pdf_path):
    """
    Loads one PDF, returns a list of page dicts:
      {source, page_number, text, ocr_used, ocr_succeeded}
    """
    filename = os.path.basename(pdf_path)
    text_pages = extract_text_pages(pdf_path)

    pages = []
    for i, text in enumerate(text_pages):
        page_number = i + 1
        ocr_used = False
        ocr_succeeded = None

        if not text.strip():
            # No text layer -- likely a scanned page. Fall back to OCR.
            ocr_used = True
            if OCR_AVAILABLE:
                try:
                    text = ocr_page(pdf_path, i)
                    ocr_succeeded = bool(text.strip())
                except Exception as e:
                    print(f"  OCR failed on {filename} page {page_number}: {e}")
                    text = ""
                    ocr_succeeded = False
            else:
                print(
                    f"  {filename} page {page_number} has no text layer, "
                    f"and OCR dependencies (pytesseract/pdf2image/tesseract/"
                    f"poppler) are not installed -- page recorded as empty, "
                    f"not skipped silently."
                )
                text = ""
                ocr_succeeded = False

        pages.append({
            "source": filename,
            "page_number": page_number,
            "text": text,
            "ocr_used": ocr_used,
            "ocr_succeeded": ocr_succeeded,
        })

    return pages


def main():
    create_output_dir()
    pdf_paths = list_documents()

    if not pdf_paths:
        print(
            "No PDFs found in documents/. Put your assigned documents "
            "there (including the scanned one) before running this."
        )
        sys.exit(1)

    print(f"Found {len(pdf_paths)} document(s) in documents/")
    if not OCR_AVAILABLE:
        print(
            "NOTE: OCR libraries not available in this environment "
            "(pip install pytesseract pdf2image, plus the tesseract-ocr "
            "and poppler-utils system packages). Any scanned/no-text-layer "
            "PDF will be recorded with empty text and ocr_succeeded=False "
            "until those are installed."
        )

    all_pages = []
    for pdf_path in pdf_paths:
        filename = os.path.basename(pdf_path)
        print(f"\nLoading {filename} ...")
        pages = load_pdf(pdf_path)
        n_ocr = sum(1 for p in pages if p["ocr_used"])
        print(f"  {len(pages)} page(s), {n_ocr} required OCR fallback")
        all_pages.extend(pages)

    out_path = save_json(
        {"ingested_date": str(date.today()), "pages": all_pages},
        "loaded_documents.json",
    )
    print(f"\nSaved {len(all_pages)} pages total to {out_path}")


if __name__ == "__main__":
    main()