import fitz  # PyMuPDF


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extract raw text from PDF bytes using PyMuPDF. Fast and accurate."""
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    except Exception as exc:
        raise ValueError(f"Failed to open PDF: {exc}") from exc

    if doc.page_count == 0:
        raise ValueError("PDF has no pages.")

    text_parts: list[str] = []
    for page in doc:
        text_parts.append(page.get_text("text"))
    doc.close()

    full_text = "\n".join(text_parts).strip()
    if not full_text:
        raise ValueError("PDF contains no extractable text (possibly scanned/image-based).")

    return full_text
