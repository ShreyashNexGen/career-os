from typing import List, Optional, Any, Dict
from pydantic import BaseModel, EmailStr
from datetime import datetime

# --- Auth Schemas ---
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: str
    full_name: str
    preferred_ai: str
    has_gemini_key: bool
    has_groq_key: bool
    created_at: datetime

    class Config:
        from_attributes = True

class UserKeysUpdate(BaseModel):
    gemini_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None
    preferred_ai: Optional[str] = "gemini"

# --- Profile Schemas ---
class ProfileUpdate(BaseModel):
    headline: Optional[str] = None
    location: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    summary: Optional[str] = None
    skills_json: Optional[str] = None
    experience_json: Optional[str] = None
    projects_json: Optional[str] = None
    education_json: Optional[str] = None
    achievements_json: Optional[str] = None

class ProfileOut(BaseModel):
    id: int
    user_id: int
    headline: Optional[str]
    location: Optional[str]
    phone: Optional[str]
    linkedin_url: Optional[str]
    github_url: Optional[str]
    portfolio_url: Optional[str]
    summary: Optional[str]
    skills_json: Optional[str]
    experience_json: Optional[str]
    projects_json: Optional[str]
    education_json: Optional[str]
    achievements_json: Optional[str]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

# --- Tailor Engine Schemas ---
class TailorRequest(BaseModel):
    job_url: Optional[str] = None
    company_name: Optional[str] = None
    role_title: Optional[str] = None
    job_description: str
    provider: Optional[str] = "gemini" # gemini, groq, offline

class TailorResponse(BaseModel):
    company_name: str
    role_title: str
    fit_score: int
    fit_summary: str
    matching_skills: List[str]
    missing_skills: List[str]
    tailored_cv_text: str
    tailored_cv_latex: str
    tailored_cover_letter: str
    outreach_linkedin_dm: str
    outreach_cold_email: str
    application_id: Optional[int] = None

# --- Application Tracking Schemas ---
class ApplicationCreate(BaseModel):
    company: str
    role: str
    status: Optional[str] = "discovered"
    fit_score: Optional[int] = 0
    contact_name: Optional[str] = None
    contact_channel: Optional[str] = None
    job_url: Optional[str] = None
    notes: Optional[str] = None

class ApplicationUpdate(BaseModel):
    status: Optional[str] = None
    fit_score: Optional[int] = None
    contact_name: Optional[str] = None
    contact_channel: Optional[str] = None
    notes: Optional[str] = None

class ApplicationOut(BaseModel):
    id: int
    company: str
    role: str
    status: str
    fit_score: int
    contact_name: Optional[str]
    contact_channel: Optional[str]
    job_url: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# --- Document Vault Schemas ---
class DocumentOut(BaseModel):
    id: int
    application_id: Optional[int]
    company: str
    role: str
    doc_type: str
    content_text: str
    latex_text: Optional[str]
    html_text: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

# --- Stats Schema ---
class StatsResponse(BaseModel):
    total_applications: int
    status_counts: Dict[str, int]
    avg_fit_score: float
    total_documents: int
