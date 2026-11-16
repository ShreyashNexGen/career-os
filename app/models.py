from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    gemini_api_key = Column(String(255), nullable=True)
    groq_api_key = Column(String(255), nullable=True)
    preferred_ai = Column(String(50), default="gemini") # gemini, groq, offline
    created_at = Column(DateTime, default=datetime.utcnow)

    profile = relationship("CandidateProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="user", cascade="all, delete-orphan")
    documents = relationship("GeneratedDocument", back_populates="user", cascade="all, delete-orphan")
    jobs = relationship("JobPosting", back_populates="user", cascade="all, delete-orphan")
    chat_sessions = relationship("AiChatSession", back_populates="user", cascade="all, delete-orphan")

class CandidateProfile(Base):
    __tablename__ = "candidate_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    headline = Column(String(255), nullable=True)
    location = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    linkedin_url = Column(String(255), nullable=True)
    github_url = Column(String(255), nullable=True)
    portfolio_url = Column(String(255), nullable=True)
    summary = Column(Text, nullable=True)
    skills_json = Column(Text, nullable=True)        # JSON array of skill strings / objects
    experience_json = Column(Text, nullable=True)    # JSON array of work experience
    projects_json = Column(Text, nullable=True)      # JSON array of technical projects
    education_json = Column(Text, nullable=True)     # JSON array of education records
    achievements_json = Column(Text, nullable=True)  # JSON array of awards/DSA rankings
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="profile")

class JobPosting(Base):
    __tablename__ = "job_postings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    title = Column(String(255), nullable=False)
    company = Column(String(255), nullable=False)
    location = Column(String(255), nullable=True)
    url = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    source = Column(String(100), default="radar")
    salary = Column(String(100), nullable=True)
    match_score = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="jobs")

class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    company = Column(String(255), nullable=False)
    role = Column(String(255), nullable=False)
    status = Column(String(50), default="discovered") # discovered, drafted, applied, interview, offer, rejected
    fit_score = Column(Integer, default=0)
    contact_name = Column(String(255), nullable=True)
    contact_channel = Column(String(100), nullable=True)
    job_url = Column(Text, nullable=True)
    jd_text = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="applications")
    documents = relationship("GeneratedDocument", back_populates="application", cascade="all, delete-orphan")

class GeneratedDocument(Base):
    __tablename__ = "generated_documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=True)
    company = Column(String(255), nullable=False)
    role = Column(String(255), nullable=False)
    doc_type = Column(String(50), nullable=False) # cv, cover_letter, outreach_dm
    content_text = Column(Text, nullable=False)
    latex_text = Column(Text, nullable=True)
    html_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="documents")
    application = relationship("Application", back_populates="documents")

class LearningProgress(Base):
    __tablename__ = "learning_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    category = Column(String(50), nullable=False, index=True) # dsa, sysdesign, corecs
    item_id = Column(String(100), nullable=False, index=True)
    status = Column(String(30), default="todo") # todo, solved, revisit
    notes = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class DailyMomentum(Base):
    __tablename__ = "daily_momentum"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    date_str = Column(String(20), nullable=False, index=True) # YYYY-MM-DD
    apps_count = Column(Integer, default=0)
    dsa_count = Column(Integer, default=0)
    design_count = Column(Integer, default=0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AiChatSession(Base):
    __tablename__ = "ai_chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False, default="New Conversation")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("AiChatMessage", back_populates="session", cascade="all, delete-orphan", order_by="AiChatMessage.id")

class AiChatMessage(Base):
    __tablename__ = "ai_chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("ai_chat_sessions.id"), nullable=False, index=True)
    role = Column(String(20), nullable=False) # user, assistant, system
    content = Column(Text, nullable=False)
    provider = Column(String(50), nullable=True) # gemini, groq, offline
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("AiChatSession", back_populates="messages")
