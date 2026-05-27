"""FastAPI route for targeted resume review (PDF upload + JD)."""

from __future__ import annotations

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from .schemas import TargetedReviewResponse
from .service import targeted_review_pipeline

router = APIRouter(prefix="/resume", tags=["Targeted Review"])

MAX_PDF_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_TYPES = {"application/pdf", "application/octet-stream"}
VALID_SENIORITY = {"junior", "mid", "senior", "staff", "principal", "director", "vp", "c-level"}


@router.post("/targeted-review", response_model=TargetedReviewResponse)
async def targeted_review(
    file: UploadFile = File(..., description="Resume PDF file"),
    job_description: str = Form(..., description="Full job description text"),
    company_name: str = Form(default=None, description="Target company name"),
    target_role: str = Form(default=None, description="Target role title"),
    seniority_level: str = Form(default=None, description="Expected seniority"),
):
    """
    Upload a resume PDF + paste a Job Description.
    Returns a comprehensive recruiter-grade targeted evaluation.
    """
    # Validate file type
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    # Validate JD
    if not job_description or not job_description.strip():
        raise HTTPException(status_code=422, detail="Job description is required.")
    if len(job_description) > 20000:
        raise HTTPException(status_code=422, detail="Job description exceeds 20,000 character limit.")

    # Read PDF bytes
    pdf_bytes = await file.read()
    if len(pdf_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    if len(pdf_bytes) > MAX_PDF_SIZE:
        raise HTTPException(status_code=413, detail="File exceeds maximum size of 10MB.")

    # Validate seniority if provided
    if seniority_level and seniority_level.lower() not in VALID_SENIORITY:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid seniority_level. Must be one of: {', '.join(sorted(VALID_SENIORITY))}",
        )

    # Run pipeline
    try:
        result = await targeted_review_pipeline(
            pdf_bytes=pdf_bytes,
            job_description=job_description,
            company_name=company_name,
            target_role=target_role,
            seniority_level=seniority_level.lower() if seniority_level else None,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Targeted review failed: {str(exc)}")

    return result
