import logging
from app.schemas import ParsedResume
from app.llm_client import get_instructor_client, get_model_name

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
You are a precise resume data extractor AND an elite resume quality evaluator.

TASK 1 — EXTRACTION:
Extract the Work Experience and Projects sections verbatim.
Rules:
- Copy text VERBATIM. Do NOT paraphrase, summarize, or infer.
- If a field is not present, return null or an empty list.
- Do NOT hallucinate companies, roles, projects, or technologies.
- Preserve original formatting of dates and descriptions.

TASK 2 — SCORING (standalone, no JD):
Infer the candidate's primary role and domain from the resume, then score it across 5 dimensions.

Scoring dimensions (total = 100):
- impact_score (max 30): Are bullets quantified? Measurable results, metrics, business outcomes.
- brevity_score (max 20): Conciseness. No filler words ("responsible for", "helped with"). Bullets ≤2 lines.
- style_score (max 20): Strong action verbs, consistent past tense (except current role), clean parallel structure.
- skills_score (max 15): Skills section relevance and depth relative to the detected role.
- sections_score (max 15): Presence of: summary/objective, skills, education, contact info.

overall_score = sum of the five section scores.

Rules:
- Be brutally honest and specific to THIS resume. No generic advice.
- top_issues: 3-5 highest-ROI fixes, most impactful first.
- strengths: 2-3 genuine standouts, not platitudes.
- Return ONLY valid JSON matching the required schema."""


def parse_resume_text(resume_text: str) -> ParsedResume:
    """Send extracted resume text to the LLM and return structured data."""
    client = get_instructor_client()
    model = get_model_name()

    logger.info("Calling LLM provider with model: %s", model)
    try:
        result = client.chat.completions.create(
            model=model,
            response_model=ParsedResume,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Extract structured data from this resume:\n\n{resume_text}"},
            ],
            max_retries=2,
        )
        return result
    except Exception as exc:
        logger.exception("LLM call failed — model=%s error=%s", model, exc)
        raise
