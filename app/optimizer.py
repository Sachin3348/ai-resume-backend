"""
Magic Writer: optimizes resume bullet points using LLM + semantic caching.
"""

import json
import logging

from app.schemas import OptimizedBullet, OptimizationResponse
from app.llm_client import get_instructor_client, get_model_name
from app.cache import semantic_check, semantic_store

logger = logging.getLogger(__name__)

# "You are a professional resume writer. For each bullet point provided, generate exactly 4 rewritten variations.\n"
# "Each variation should:\n"
# "- Start with a different strong action verb\n"
# "- Quantify with metrics where possible\n"
# "- Be concise (under 25 words)\n"
# "- Preserve the original factual meaning exactly\n"
# "Do NOT invent achievements or metrics not implied by the original.\n"
# "Return exactly 4 suggestions per bullet."

OPTIMIZE_SYSTEM_PROMPT = (
    """
        You are an expert technical resume writer. For each provided bullet point, generate exactly 4 optimized variations.

        RULES:
        1. Action-First: Start each variation with a distinct, high-impact action verb. 
        2. The X-Y-Z Formula: Structure variations as "Accomplished [X] as measured by [Y], by doing [Z]".
        3. The Metric Rule: NEVER invent facts or numbers. If original text lacks metrics, you MUST insert bracketed placeholders (e.g., `[X]%`, `[$Y]`) for the user to fill.
        4. Brevity: Max 25 words per variation. Remove pronouns.
        5. Strict Schema: Output ONLY the requested JSON structure. No explanations."""
)


def _build_prompt(role: str, company: str, bullet: str) -> str:
    """Build a consistent prompt key for semantic caching."""
    return f"role:{role}|company:{company}|bullet:{bullet}"


def optimize_bullets(role: str, company: str, bullets: list[str]) -> OptimizationResponse:
    """
    Optimize bullet points with semantic cache bypass.
    Only cache-miss bullets are sent to the LLM.
    """
    results: list[OptimizedBullet] = []
    cache_misses: list[tuple[int, str]] = []  # (index, bullet)

    # Phase 1: Check semantic cache for each bullet
    for idx, bullet in enumerate(bullets):
        prompt_key = _build_prompt(role, company, bullet)
        cached = semantic_check(prompt_key)

        if cached:
            logger.info("Semantic HIT for bullet[%d]", idx)
            try:
                obj = OptimizedBullet.model_validate_json(cached)
                results.append(obj)
            except Exception:
                # Corrupted cache entry — treat as miss
                cache_misses.append((idx, bullet))
                results.append(None)  # type: ignore[arg-type]
        else:
            logger.info("Semantic MISS for bullet[%d]", idx)
            cache_misses.append((idx, bullet))
            results.append(None)  # type: ignore[arg-type]

    # Phase 2: Call LLM only for misses
    if cache_misses:
        miss_bullets = [b for _, b in cache_misses]
        llm_results = _call_llm_for_bullets(role, company, miss_bullets)

        # Phase 3: Merge LLM results back and store in cache
        for i, (idx, bullet) in enumerate(cache_misses):
            optimized = llm_results[i] if i < len(llm_results) else OptimizedBullet(
                original=bullet, optimized=bullet
            )
            results[idx] = optimized

            # Store in semantic cache
            prompt_key = _build_prompt(role, company, bullet)
            semantic_store(prompt_key, optimized.model_dump_json())

    return OptimizationResponse(results=results)


def _call_llm_for_bullets(role: str, company: str, bullets: list[str]) -> list[OptimizedBullet]:
    """Batch-call LLM for a list of bullet points."""
    client = get_instructor_client()
    model = get_model_name()

    bullet_text = "\n".join(f"- {b}" for b in bullets)
    user_msg = (
        f"Role: {role}\nCompany: {company}\n\n"
        f"Optimize these bullet points:\n{bullet_text}"
    )

    logger.info("Calling LLM for %d bullet(s) — model=%s", len(bullets), model)
    try:
        response = client.chat.completions.create(
            model=model,
            response_model=OptimizationResponse,
            messages=[
                {"role": "system", "content": OPTIMIZE_SYSTEM_PROMPT},
                {"role": "user", "content": user_msg},
            ],
            max_retries=2,
        )
        return response.results
    except Exception as exc:
        logger.exception("LLM optimization failed: %s", exc)
        # Graceful fallback: return originals unchanged
        return [OptimizedBullet(original=b, suggestions=[b, b, b, b]) for b in bullets]
