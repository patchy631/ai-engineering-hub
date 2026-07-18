from pydantic import BaseModel, Field
from typing import Optional, List


class ContactInfo(BaseModel):
    """Contact information model."""

    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[str] = None
    portfolio: Optional[str] = None


class WorkExperience(BaseModel):
    """Work experience entry model."""

    company: str
    title: str
    dates: Optional[str] = None
    location: Optional[str] = None
    bullets: List[str] = Field(default_factory=list)


class Education(BaseModel):
    """Education entry model."""

    institution: str
    degree: Optional[str] = None
    field: Optional[str] = None
    graduation_date: Optional[str] = None
    gpa: Optional[str] = None


class Project(BaseModel):
    """Project entry model."""

    name: str
    description: Optional[str] = None
    technologies: List[str] = Field(default_factory=list)
    outcomes: Optional[str] = None


class Certification(BaseModel):
    """Certification entry model."""

    name: str
    issuer: Optional[str] = None
    date: Optional[str] = None


class ParsedResume(BaseModel):
    """Structured resume data model."""

    contact_info: ContactInfo = Field(default_factory=ContactInfo)
    summary: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    experience: List[WorkExperience] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    projects: List[Project] = Field(default_factory=list)
    certifications: List[Certification] = Field(default_factory=list)


class JobDescription(BaseModel):
    """Structured job description model."""

    job_title: Optional[str] = None
    company_name: Optional[str] = None
    responsibilities: List[str] = Field(default_factory=list)
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    seniority_level: Optional[str] = None
    years_experience: Optional[str] = None
    location_requirements: Optional[str] = None
    education_requirements: Optional[str] = None


class KeywordCoverage(BaseModel):
    """Keyword coverage analysis model."""

    matched_keywords: List[str] = Field(default_factory=list)
    unmatched_keywords: List[str] = Field(default_factory=list)


class ResumeAnalysis(BaseModel):
    """Resume-job match analysis model."""

    keyword_coverage: KeywordCoverage = Field(default_factory=KeywordCoverage)
    missing_skills: List[str] = Field(default_factory=list)
    experience_alignment: Optional[str] = None
    skill_gaps: List[str] = Field(default_factory=list)
    strengths: List[str] = Field(default_factory=list)
    optimization_opportunities: List[str] = Field(default_factory=list)


class OptimizedResume(BaseModel):
    """Optimized resume data model (same structure as ParsedResume)."""

    contact_info: ContactInfo = Field(default_factory=ContactInfo)
    summary: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    experience: List[WorkExperience] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    projects: List[Project] = Field(default_factory=list)
    certifications: List[Certification] = Field(default_factory=list)
