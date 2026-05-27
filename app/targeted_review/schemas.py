"""Pydantic schemas for targeted resume review."""

from __future__ import annotations

from pydantic import BaseModel, Field


class GapAnalysis(BaseModel):
    matched_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    weak_match_areas: list[str] = Field(default_factory=list)
    overrepresented_skills: list[str] = Field(default_factory=list)
    underrepresented_requirements: list[str] = Field(default_factory=list)


class KeywordAnalysis(BaseModel):
    keyword_match_percentage: int = Field(ge=0, le=100)
    missing_keywords: list[str] = Field(default_factory=list)
    high_priority_keywords: list[str] = Field(default_factory=list)
    ats_risk_factors: list[str] = Field(default_factory=list)
    keyword_integration_suggestions: list[str] = Field(default_factory=list)


class OptimizedBullet(BaseModel):
    original: str
    optimized: str
    reason: str


class ExperienceAnalysis(BaseModel):
    experience_alignment_score: int = Field(ge=0, le=100)
    recruiter_confidence: str
    missing_proof_points: list[str] = Field(default_factory=list)
    optimized_bullets: list[OptimizedBullet] = Field(default_factory=list)


class ProjectAnalysis(BaseModel):
    project_relevance_score: int = Field(ge=0, le=100)
    technical_depth_assessment: str = ""
    missing_project_signals: list[str] = Field(default_factory=list)
    suggested_projects_to_add: list[str] = Field(default_factory=list)


class SectionDetail(BaseModel):
    score: int = Field(ge=0)
    max_score: int
    issues: list[str] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    jd_alignment_feedback: str = ""
    recruiter_perception: str = ""
    optimized_example: str = ""
    improvement_suggestions: list[str] = Field(default_factory=list)


class SectionScores(BaseModel):
    headline: SectionDetail
    summary: SectionDetail
    experience: SectionDetail
    projects: SectionDetail
    skills: SectionDetail
    ats_optimization: SectionDetail
    keyword_optimization: SectionDetail
    recruiter_readiness: SectionDetail


class RecruiterPsychology(BaseModel):
    first_impression: str = ""
    ownership_signals: str = ""
    differentiation_assessment: str = ""
    red_flags: list[str] = Field(default_factory=list)
    hidden_strengths: list[str] = Field(default_factory=list)
    hiring_probability_narrative: str = ""


class RewriteSuggestions(BaseModel):
    headline: str = ""
    summary: str = ""
    skills_positioning: str = ""
    experience_bullets: list[OptimizedBullet] = Field(default_factory=list)


class StrategicInsights(BaseModel):
    biggest_problem: str
    highest_roi_fix: str
    top_3_improvements: list[str] = Field(min_length=3, max_length=3)
    fastest_score_boosters: list[str] = Field(default_factory=list)
    recruiter_red_flags: list[str] = Field(default_factory=list)
    missing_proof_points: list[str] = Field(default_factory=list)
    hidden_strengths: list[str] = Field(default_factory=list)


class EducationalInsight(BaseModel):
    title: str
    explanation: str
    why_it_matters: str
    actionable_tip: str


class TargetedReviewData(BaseModel):
    overall_match_score: int = Field(ge=0, le=100)
    ats_match_score: int = Field(ge=0, le=100)
    recruiter_match_score: int = Field(ge=0, le=100)
    technical_alignment_score: int = Field(ge=0, le=100)
    experience_relevance_score: int = Field(ge=0, le=100)
    competitiveness_score: int = Field(ge=0, le=100)
    hiring_probability_estimate: str

    detected_domain: str
    target_role_alignment: str
    seniority_fit: str
    market_competitiveness: str
    current_market_signal: str

    gap_analysis: GapAnalysis
    keyword_analysis: KeywordAnalysis
    experience_analysis: ExperienceAnalysis
    project_analysis: ProjectAnalysis
    section_scores: SectionScores
    recruiter_psychology: RecruiterPsychology
    rewrite_suggestions: RewriteSuggestions
    strategic_insights: StrategicInsights
    educational_insights: list[EducationalInsight] = Field(min_length=2, max_length=5)


class TargetedReviewResponse(BaseModel):
    success: bool = True
    data: TargetedReviewData
