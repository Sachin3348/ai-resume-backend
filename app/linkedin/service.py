"""LinkedIn review business logic / service layer."""

from __future__ import annotations

from .pdf_extractor import normalize_linkedin_pdf
from .section_parser import parse_linkedin_profile
from .prompts import LINKEDIN_EVALUATION_SYSTEM_PROMPT, LINKEDIN_EVALUATION_USER_PROMPT
from .ai_providers import get_ai_provider
from .schemas import LinkedInEvaluation, LinkedInReviewResponse


async def review_linkedin_profile(pdf_bytes: bytes) -> LinkedInReviewResponse:
    """
    Full pipeline:
    1. Extract text from PDF
    2. Parse sections
    3. Build prompt
    4. Call AI
    5. Return validated response
    """
    # Step 1: Extract
    text = normalize_linkedin_pdf(pdf_bytes)

    # Step 2: Parse
    profile = parse_linkedin_profile(text)

    # Step 3: Build prompt
    user_prompt = LINKEDIN_EVALUATION_USER_PROMPT.format(
        name=profile.name or "Unknown",
        headline=profile.headline or "Not provided",
        location=profile.location or "Not provided",
        profile_text=profile.raw_text[:12000],  # Limit token usage
    )

    # Step 4: AI evaluation
    provider = get_ai_provider()
    evaluation = await provider.evaluate_profile(
        system_prompt=LINKEDIN_EVALUATION_SYSTEM_PROMPT,
        user_prompt=user_prompt,
    )

    # Step 5: Return
    return LinkedInReviewResponse(success=True, data=evaluation)
