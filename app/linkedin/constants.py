"""LinkedIn review module constants."""

MAX_PDF_SIZE_MB = 10
MAX_PDF_SIZE_BYTES = MAX_PDF_SIZE_MB * 1024 * 1024

SUPPORTED_CONTENT_TYPES = (
    "application/pdf",
    "application/octet-stream",
)

# Section detection headers (case-insensitive matching)
LINKEDIN_SECTIONS = [
    "about",
    "summary",
    "experience",
    "education",
    "skills",
    "certifications",
    "licenses & certifications",
    "projects",
    "honors & awards",
    "achievements",
    "publications",
    "courses",
    "volunteering",
    "volunteer experience",
    "recommendations",
    "featured",
    "languages",
    "interests",
    "organizations",
]

# Scoring weights
SCORING_WEIGHTS = {
    "headline": 15,
    "summary": 15,
    "experience": 30,
    "keywords": 15,
    "positioning": 10,
    "completeness": 10,
    "searchability": 5,
}
