"""LinkedIn review API routes."""

from __future__ import annotations

from fastapi import APIRouter, File, UploadFile, HTTPException

from .constants import SUPPORTED_CONTENT_TYPES, MAX_PDF_SIZE_BYTES
from .schemas import LinkedInReviewResponse
from .service import review_linkedin_profile

router = APIRouter(prefix="/linkedin", tags=["LinkedIn"])


@router.post("/review", response_model=LinkedInReviewResponse)
async def linkedin_review(
    file: UploadFile = File(..., description="LinkedIn profile PDF"),
):
    """
    Upload a LinkedIn profile PDF and receive a recruiter-grade
    structured evaluation with scoring and actionable recommendations.
    """
    # Validate content type
    if file.content_type not in SUPPORTED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    # Read and validate size
    pdf_bytes = await file.read()
    if len(pdf_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    if len(pdf_bytes) > MAX_PDF_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds maximum size of {MAX_PDF_SIZE_BYTES // (1024*1024)}MB.",
        )

    # Run pipeline
    try:
        result = await review_linkedin_profile(pdf_bytes)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"AI evaluation failed: {str(exc)}",
        )

    return result
