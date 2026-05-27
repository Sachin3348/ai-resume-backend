"""Orchestrator: PDF extraction -> cache check -> LLM -> cache store."""

from __future__ import annotations

import asyncio
import hashlib
import logging
from functools import partial

from app.cache import cache_get, cache_set, hash_text
from app.config import get_settings
from app.pdf_extractor import extract_text_from_pdf
from app.targeted_review.ai_service import run_targeted_review_llm
from app.targeted_review.schemas import TargetedReviewData, TargetedReviewResponse

logger = logging.getLogger(__name__)

CACHE_PREFIX = "targeted_review"


def _build_cache_key(resume_text: str, jd: str, role: str, company: str) -> str:
    content = f"{resume_text}|{jd}|{role}|{company}"
    return f"{CACHE_PREFIX}:{hashlib.sha256(content.encode()).hexdigest()}"


async def targeted_review_pipeline(
    pdf_bytes: bytes,
    job_description: str,
    company_name: str | None = None,
    target_role: str | None = None,
    seniority_level: str | None = None,
) -> TargetedReviewResponse:
    """Full pipeline: extract PDF -> check cache -> LLM -> store -> return."""

    # Step 1: Extract text from PDF
    resume_text = extract_text_from_pdf(pdf_bytes)

    # Normalize inputs
    company = company_name or "Not specified"
    role = target_role or "Not specified"
    seniority = seniority_level or "Not specified"
    jd = job_description.strip()

    # Step 2: Check exact-match cache
    cache_key = _build_cache_key(resume_text, jd, role, company)
    cached = cache_get(cache_key)
    if cached:
        logger.info("Targeted review cache HIT")
        data = TargetedReviewData.model_validate_json(cached)
        return TargetedReviewResponse(success=True, data=data)

    logger.info("Targeted review cache MISS - calling LLM")

    # Step 3: Call LLM (sync instructor, run in thread)
    loop = asyncio.get_running_loop()
    data = await loop.run_in_executor(
        None,
        partial(
            run_targeted_review_llm,
            resume_text=resume_text,
            job_description=jd,
            company_name=company,
            target_role=role,
            seniority_level=seniority,
        ),
    )

    # Step 4: Store in cache
    settings = get_settings()
    cache_set(cache_key, data.model_dump_json(), ttl_seconds=settings.cache_ttl_days * 86400)

    return TargetedReviewResponse(success=True, data=data)
