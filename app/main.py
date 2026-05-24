from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse

from app.schemas import ParsedResume
from app.pdf_extractor import extract_text_from_pdf
from app.parser import parse_resume_text
from app.llm_client import get_instructor_client

app = FastAPI(
    title="AI Resume Parser",
    version="1.0.0",
)


@app.on_event("startup")
async def startup_event():
    """Eagerly initialize the LLM client to catch missing API keys at boot."""
    get_instructor_client()


@app.post("/parse-resume", response_model=ParsedResume)
async def parse_resume(file: UploadFile = File(..., description="PDF resume file")):
    # Validate content type
    if file.content_type not in ("application/pdf", "application/octet-stream"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    # Read file bytes
    pdf_bytes = await file.read()
    if len(pdf_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    # Extract text from PDF
    try:
        resume_text = extract_text_from_pdf(pdf_bytes)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    # Parse with LLM
    try:
        parsed = parse_resume_text(resume_text)
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"LLM parsing failed: {exc}",
        )

    return parsed


@app.get("/health")
async def health():
    return {"status": "ok"}
