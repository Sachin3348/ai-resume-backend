"""Pydantic schemas for LinkedIn profile review."""

from __future__ import annotations
from pydantic import BaseModel, Field


# --- Request / internal models ---

class LinkedInSection(BaseModel):
    name: str
    content: str


class ExtractedProfile(BaseModel):
    raw_text: str
    name: str | None = None
    headline: str | None = None
    location: str | None = None
    sections: list[LinkedInSection] = Field(default_factory=list)


# --- AI evaluation response models ---

class HeadlineScore(BaseModel):
    score: int = Field(..., ge=0, le=15)
    issues: list[str]
    optimized_example: str


class SummaryScore(BaseModel):
    score: int = Field(..., ge=0, le=15)
    issues: list[str]
    optimized_example: str


class ExperienceScore(BaseModel):
    score: int = Field(..., ge=0, le=30)
    issues: list[str]
    optimized_example: str


class KeywordsScore(BaseModel):
    score: int = Field(..., ge=0, le=15)
    missing_keywords: list[str]
    recommendations: list[str]


class PositioningScore(BaseModel):
    score: int = Field(..., ge=0, le=10)
    issues: list[str]
    recommendations: list[str]


class CompletenessScore(BaseModel):
    score: int = Field(..., ge=0, le=10)
    missing_sections: list[str]
    recommendations: list[str]


class SearchabilityScore(BaseModel):
    score: int = Field(..., ge=0, le=5)
    issues: list[str]
    recommendations: list[str]


class SectionScores(BaseModel):
    headline: HeadlineScore
    summary: SummaryScore
    experience: ExperienceScore
    keywords: KeywordsScore
    positioning: PositioningScore
    completeness: CompletenessScore
    searchability: SearchabilityScore


class LinkedInEvaluation(BaseModel):
    detected_domain: str
    seniority_level: str
    primary_specialization: str
    overall_score: int = Field(..., ge=0, le=100)
    market_competitiveness: str
    current_market_signal: str
    biggest_problem: str
    highest_roi_fix: str
    section_scores: SectionScores
    top_3_improvements: list[str] = Field(..., min_length=3, max_length=3)


# --- API response ---

class LinkedInReviewResponse(BaseModel):
    success: bool = True
    data: LinkedInEvaluation
