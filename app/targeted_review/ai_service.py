"""AI service for targeted resume review using instructor."""

import logging

from app.llm_client import get_instructor_client, get_model_name
from app.targeted_review.prompts import (
    TARGETED_REVIEW_SYSTEM_PROMPT,
    TARGETED_REVIEW_USER_PROMPT,
)
from app.targeted_review.schemas import TargetedReviewData

logger = logging.getLogger(__name__)


def run_targeted_review_llm(
    resume_text: str,
    job_description: str,
    company_name: str = "Not specified",
    target_role: str = "Not specified",
    seniority_level: str = "Not specified",
) -> TargetedReviewData:
    """Call LLM with resume + JD and return structured evaluation."""

    client = get_instructor_client()
    model = get_model_name()

    user_prompt = TARGETED_REVIEW_USER_PROMPT.format(
        company_name=company_name,
        target_role=target_role,
        seniority_level=seniority_level,
        job_description=job_description[:6000],
        resume_text=resume_text[:8000],
    )

    logger.info(
        "Targeted review LLM call: model=%s, resume=%d chars, jd=%d chars",
        model, len(resume_text), len(job_description),
    )

    result = client.chat.completions.create(
        model=model,
        response_model=TargetedReviewData,
        messages=[
            {"role": "system", "content": TARGETED_REVIEW_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        max_retries=2,
    )

    return result
