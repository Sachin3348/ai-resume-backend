from pydantic import BaseModel, Field


class WorkExperience(BaseModel):
    """A single work experience entry extracted verbatim from the resume."""

    company: str = Field(
        ...,
        description="Exact company or organization name as written on the resume. Do NOT infer or guess.",
    )
    role: str = Field(
        ...,
        description="Exact job title or designation as written on the resume. Do NOT paraphrase.",
    )
    start_date: str | None = Field(
        default=None,
        description="Start date as written on the resume (e.g., 'Jan 2022', '2021'). Return null if not present.",
    )
    end_date: str | None = Field(
        default=None,
        description="End date as written (e.g., 'Present', 'Dec 2023'). Return null if not present.",
    )
    location: str | None = Field(
        default=None,
        description="Work location as stated on the resume. Return null if not mentioned.",
    )
    bullets: list[str] = Field(
        default_factory=list,
        description="List of responsibility/achievement bullet points copied verbatim from the resume. Do NOT summarize or fabricate.",
    )


class Project(BaseModel):
    """A single project entry extracted verbatim from the resume."""

    name: str = Field(
        ...,
        description="Exact project name or title as written on the resume. Do NOT infer.",
    )
    description: str | None = Field(
        default=None,
        description="Project description exactly as stated. Return null if not present. Do NOT generate descriptions.",
    )
    technologies: list[str] = Field(
        default_factory=list,
        description="Technologies/tools explicitly listed for this project. Only include what is written.",
    )
    url: str | None = Field(
        default=None,
        description="Project URL/link if explicitly provided. Return null otherwise.",
    )
    bullets: list[str] = Field(
        default_factory=list,
        description="Achievement or detail bullet points copied verbatim. Do NOT fabricate.",
    )


class ParsedResume(BaseModel):
    """Structured extraction of Work Experience and Projects sections from a resume."""

    work_experience: list[WorkExperience] = Field(
        default_factory=list,
        description="All work experience entries found in the resume. Return empty list if no work experience section exists.",
    )
    projects: list[Project] = Field(
        default_factory=list,
        description="All project entries found in the resume. Return empty list if no projects section exists.",
    )


# ---------------------------------------------------------------------------
# Optimization Schemas (Magic Writer)
# ---------------------------------------------------------------------------


class OptimizedBullet(BaseModel):
    """A single bullet with multiple optimized suggestions."""

    original: str = Field(
        ...,
        description="The original bullet point text exactly as provided by the user.",
    )
    suggestions: list[str] = Field(
        ...,
        min_length=4,
        max_length=4,
        description="Exactly 4 rewritten variations of the bullet point. Each uses strong action verbs, quantified impact, and concise professional language. Must preserve the factual meaning.",
    )


class OptimizationRequest(BaseModel):
    """Input for the bullet point optimizer."""

    role: str = Field(..., description="Job role/title for context.")
    company: str = Field(..., description="Company name for context.")
    bullets: list[str] = Field(
        ...,
        min_length=1,
        max_length=20,
        description="List of bullet points to optimize (1-20).",
    )


class OptimizationResponse(BaseModel):
    """Structured response from the bullet optimizer."""

    results: list[OptimizedBullet] = Field(
        ...,
        description="List of optimized bullets in the same order as input.",
    )
