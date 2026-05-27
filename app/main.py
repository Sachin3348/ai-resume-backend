from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse

from app.schemas import ParsedResume, OptimizationRequest, OptimizationResponse
from app.pdf_extractor import extract_text_from_pdf
from app.parser import parse_resume_text
from app.optimizer import optimize_bullets
from app.llm_client import get_instructor_client
from app.cache import hash_text, cache_get, cache_set, warm_up_cache
from app.linkedin.router import router as linkedin_router
from app.targeted_review.router import router as targeted_review_router

app = FastAPI(
    title="AI Resume Parser",
    version="1.0.0",
)

app.include_router(linkedin_router)
app.include_router(targeted_review_router)


@app.on_event("startup")
async def startup_event():
    """Eagerly initialize singletons to catch config errors at boot."""
    get_instructor_client()
    warm_up_cache()  # loads embedding model once, connects Redis, creates index


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

    # --- Exact-match cache lookup ---
    text_hash = hash_text(resume_text)
    cache_key = f"resume:parse:{text_hash}"
    cached_json = cache_get(cache_key)

    if cached_json:
        return ParsedResume.model_validate_json(cached_json)

    # --- Cache MISS: call LLM ---
    try:
        parsed = parse_resume_text(resume_text)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"LLM parsing failed: {exc}")

    # Store in cache
    cache_set(cache_key, parsed.model_dump_json())

    return parsed


@app.post("/optimize-experience", response_model=OptimizationResponse)
async def optimize_experience(request: OptimizationRequest):
    """Optimize bullet points using LLM + semantic caching."""
    try:
        result = optimize_bullets(
            role=request.role,
            company=request.company,
            bullets=request.bullets,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Optimization failed: {exc}")

    return result


@app.get("/health")
async def health():
    return {"status": "ok"}
