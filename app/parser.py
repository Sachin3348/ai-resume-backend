import logging
from app.schemas import ParsedResume
from app.llm_client import get_instructor_client, get_model_name

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are a precise resume data extractor. "
    "Extract ONLY the Work Experience and Projects sections from the provided resume text. "
    "Rules:\n"
    "- Copy text VERBATIM from the resume. Do NOT paraphrase, summarize, or infer.\n"
    "- If a field is not explicitly present, return null or an empty list.\n"
    "- Do NOT hallucinate companies, roles, projects, or technologies that are not in the text.\n"
    "- Preserve original formatting of dates and descriptions."
)


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
