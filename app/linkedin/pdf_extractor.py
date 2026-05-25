"""Robust PDF text extraction with fallback."""

from __future__ import annotations

import re


def extract_with_pymupdf(pdf_bytes: bytes) -> str:
    """Primary extraction using PyMuPDF (fitz)."""
    import fitz

    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pages: list[str] = []
    for page in doc:
        pages.append(page.get_text("text"))
    doc.close()
    return "\n".join(pages)


def extract_with_pdfplumber(pdf_bytes: bytes) -> str:
    """Fallback extraction using pdfplumber."""
    import pdfplumber
    import io

    pages: list[str] = []
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                pages.append(text)
    return "\n".join(pages)


def clean_text(text: str) -> str:
    """Normalize whitespace and remove artifacts."""
    # Collapse multiple blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Collapse multiple spaces
    text = re.sub(r"[ \t]{2,}", " ", text)
    # Strip lines
    lines = [line.strip() for line in text.splitlines()]
    # Remove repeated header/footer patterns (e.g. "Page X of Y")
    lines = [l for l in lines if not re.match(r"^Page\s+\d+\s+of\s+\d+$", l, re.IGNORECASE)]
    return "\n".join(lines).strip()


def normalize_linkedin_pdf(pdf_bytes: bytes) -> str:
    """
    Extract and clean text from a LinkedIn PDF.
    Uses pymupdf as primary, pdfplumber as fallback.
    Raises ValueError if no extractable text found.
    """
    text = ""

    # Primary
    try:
        text = extract_with_pymupdf(pdf_bytes)
    except Exception:
        pass

    # Fallback
    if not text or len(text.strip()) < 50:
        try:
            text = extract_with_pdfplumber(pdf_bytes)
        except Exception:
            pass

    if not text or len(text.strip()) < 50:
        raise ValueError(
            "Could not extract meaningful text from PDF. "
            "The file may be scanned/image-only or corrupted."
        )

    return clean_text(text)
