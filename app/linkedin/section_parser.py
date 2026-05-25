"""Intelligent LinkedIn section detection and parsing."""

from __future__ import annotations

import re
from .constants import LINKEDIN_SECTIONS
from .schemas import ExtractedProfile, LinkedInSection


def _build_section_pattern() -> re.Pattern:
    """Build regex to match LinkedIn section headers."""
    escaped = [re.escape(s) for s in LINKEDIN_SECTIONS]
    pattern = r"^(" + "|".join(escaped) + r")\s*$"
    return re.compile(pattern, re.IGNORECASE | re.MULTILINE)


_SECTION_RE = _build_section_pattern()


def _detect_name_and_headline(lines: list[str]) -> tuple[str | None, str | None, str | None]:
    """
    Heuristic: first non-empty line is name, second is headline,
    third may be location (if it contains comma or common patterns).
    """
    non_empty = [l for l in lines[:10] if l.strip()]
    name = non_empty[0] if len(non_empty) > 0 else None
    headline = non_empty[1] if len(non_empty) > 1 else None
    location = None
    if len(non_empty) > 2:
        candidate = non_empty[2]
        # Location heuristic: contains comma or "area" or known patterns
        if "," in candidate or re.search(r"\b(area|region|country|state)\b", candidate, re.I):
            location = candidate
    return name, headline, location


def detect_sections(text: str) -> list[LinkedInSection]:
    """Detect and extract LinkedIn sections from cleaned text."""
    lines = text.splitlines()
    sections: list[LinkedInSection] = []
    current_header: str | None = None
    current_lines: list[str] = []

    for line in lines:
        stripped = line.strip()
        if _SECTION_RE.match(stripped):
            # Save previous section
            if current_header is not None:
                content = "\n".join(current_lines).strip()
                if content:
                    sections.append(LinkedInSection(name=current_header.lower(), content=content))
            current_header = stripped
            current_lines = []
        elif current_header is not None:
            current_lines.append(line)

    # Final section
    if current_header is not None:
        content = "\n".join(current_lines).strip()
        if content:
            sections.append(LinkedInSection(name=current_header.lower(), content=content))

    return sections


def parse_experience(sections: list[LinkedInSection]) -> str:
    """Extract experience content."""
    for s in sections:
        if s.name == "experience":
            return s.content
    return ""


def parse_skills(sections: list[LinkedInSection]) -> str:
    """Extract skills content."""
    for s in sections:
        if s.name == "skills":
            return s.content
    return ""


def parse_summary(sections: list[LinkedInSection]) -> str:
    """Extract about/summary content."""
    for s in sections:
        if s.name in ("about", "summary"):
            return s.content
    return ""


def parse_linkedin_profile(text: str) -> ExtractedProfile:
    """Full parsing pipeline: detect header info + sections."""
    lines = text.splitlines()
    name, headline, location = _detect_name_and_headline(lines)
    sections = detect_sections(text)

    return ExtractedProfile(
        raw_text=text,
        name=name,
        headline=headline,
        location=location,
        sections=sections,
    )
