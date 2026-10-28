import os
import json
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, PlainTextResponse
from sqlalchemy.orm import Session

from .database import engine, Base, get_db
from .models import User, CandidateProfile, JobPosting, Application, GeneratedDocument
from .auth import hash_password, verify_password, create_access_token, get_current_user
from .schemas import (
    UserRegister, UserLogin, UserOut, UserKeysUpdate,
    ProfileUpdate, ProfileOut,
    TailorRequest, TailorResponse,
    ApplicationCreate, ApplicationUpdate, ApplicationOut,
    DocumentOut, StatsResponse
)
from .services.ai_service import AIService
from .services.job_service import JobService

# Initialize SQLite tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CareerOS - Multi-User AI Job Search & Application Platform",
    version="1.0.0",
    description="SaaS platform for automated job discovery, free AI tailoring, and pipeline tracking."
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# ==========================================
# SEEDING INITIAL USER (Shreyash Shukla)
# ==========================================
@app.on_event("startup")
def seed_data():
    db = next(get_db())
    existing = db.query(User).filter(User.email == "shreyashshukla7398554573@gmail.com").first()
    if not existing:
        shreyash = User(
            email="shreyashshukla7398554573@gmail.com",
            password_hash=hash_password("admin123"),
            full_name="Shreyash Shukla",
            preferred_ai="gemini"
        )
        db.add(shreyash)
        db.commit()
        db.refresh(shreyash)

        # Profile
        profile = CandidateProfile(
            user_id=shreyash.id,
            headline="Backend / Full Stack Software Engineer | Node.js • Python • Microservices • SQL & NoSQL • AWS",
            location="Noida / Ghaziabad, UP, India (Open to Bengaluru & Remote)",
            phone="+91 6306211105",
            linkedin_url="https://linkedin.com/in/shuklashreyash",
            github_url="https://github.com/shreyash418",
            portfolio_url="https://github.com/shreyash418",
            summary="Backend-focused Software Engineer with 2+ years of production experience architecting 250+ RESTful APIs and scalable enterprise ERP platforms.",
            skills_json=json.dumps([
                "Node.js", "Express.js", "Python (Flask)", "TypeScript", "JavaScript",
                "MySQL", "MS SQL Server", "MongoDB", "Redis", "Docker", "AWS", "REST APIs",
                "Data Structures & Algorithms", "System Design (HLD/LLD)"
            ]),
            experience_json=json.dumps([
                {
                    "company": "NexGen",
                    "role": "Software Developer (Enterprise Backend)",
                    "period": "July 2024 - Present",
                    "bullets": [
                        "Architected and maintain 250+ RESTful APIs for core Enterprise ERP platforms.",
                        "Optimized SQL query indexes and execution plans, achieving 35% latency reduction.",
                        "Built Automated Reconciliation Engine in Python, cutting manual accounting by 70%.",
                        "Sustained 99.9% uptime SLA across Docker microservices with Redis caching."
                    ]
                },
                {
                    "company": "Oasis InfoByte",
                    "role": "SDE Intern (Web Products)",
                    "period": "Feb 2024 - June 2024",
                    "bullets": [
                        "Delivered 5+ e-commerce modules in React & TypeScript, cutting load time by 25%."
                    ]
                }
            ]),
            achievements_json=json.dumps([
                "Solved 800+ DSA problems; Ranked 28th out of 8,000+ users on GeeksforGeeks.",
                "8th position among 70+ teams in KAVACH National Cyber Security Hackathon."
            ])
        )
        db.add(profile)

        # Pre-seed ViralMe application
        app1 = Application(
            user_id=shreyash.id,
            company="ViralMe",
            role="Founding Backend & Full Stack Engineer",
            status="drafted",
            fit_score=94,
            contact_name="Anurag Jhaver (Founder)",
            contact_channel="LinkedIn / Founder Outreach",
            job_url="https://viralme.club",
            notes="Pre-seed backed by iSeed & Bharat Founders Fund. 30%+ WoW growth. Heavy ESOPs."
        )
        db.add(app1)
        db.commit()

        # Seed friend demo user
        friend = User(
            email="friend@example.com",
            password_hash=hash_password("demo123"),
            full_name="Alex Friend",
            preferred_ai="gemini"
        )
        db.add(friend)
        db.commit()
        db.refresh(friend)

        friend_profile = CandidateProfile(
            user_id=friend.id,
            headline="Full Stack Software Developer | React • Node.js • TypeScript",
            location="Bengaluru, India",
            phone="+91 9876543210",
            skills_json=json.dumps(["React", "Node.js", "TypeScript", "PostgreSQL", "Tailwind CSS"])
        )
        db.add(friend_profile)
        db.commit()

# ==========================================
# AUTH ENDPOINTS
# ==========================================
@app.post("/api/auth/register", response_model=UserOut)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = User(
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        full_name=user_data.full_name
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Empty profile
    profile = CandidateProfile(user_id=new_user.id, headline="Software Engineer")
    db.add(profile)
    db.commit()

    return UserOut(
        id=new_user.id,
        email=new_user.email,
        full_name=new_user.full_name,
        preferred_ai=new_user.preferred_ai,
        has_gemini_key=bool(new_user.gemini_api_key),
        has_groq_key=bool(new_user.groq_api_key),
        created_at=new_user.created_at
    )

@app.post("/api/auth/login")
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    token = create_access_token(data={"sub": user.email, "user_id": user.id})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "preferred_ai": user.preferred_ai
        }
    }

@app.get("/api/auth/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return UserOut(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        preferred_ai=current_user.preferred_ai,
        has_gemini_key=bool(current_user.gemini_api_key),
        has_groq_key=bool(current_user.groq_api_key),
        created_at=current_user.created_at
    )

@app.post("/api/settings/keys")
def update_keys(keys_data: UserKeysUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if keys_data.gemini_api_key is not None:
        current_user.gemini_api_key = keys_data.gemini_api_key.strip()
    if keys_data.groq_api_key is not None:
        current_user.groq_api_key = keys_data.groq_api_key.strip()
    if keys_data.preferred_ai is not None:
        current_user.preferred_ai = keys_data.preferred_ai
    db.commit()
    return {"status": "success", "message": "API keys updated successfully"}

# ==========================================
# CANDIDATE PROFILE ENDPOINTS
# ==========================================
@app.get("/api/profile", response_model=ProfileOut)
def get_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first()
    if not profile:
        profile = CandidateProfile(user_id=current_user.id, headline="Software Engineer")
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile

@app.put("/api/profile", response_model=ProfileOut)
def update_profile(profile_data: ProfileUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first()
    if not profile:
        profile = CandidateProfile(user_id=current_user.id)
        db.add(profile)
    
    for field, val in profile_data.dict(exclude_unset=True).items():
        setattr(profile, field, val)
    
    db.commit()
    db.refresh(profile)
    return profile

# ==========================================
# AI TAILOR ENGINE (The Core Feature)
# ==========================================
@app.post("/api/tailor", response_model=TailorResponse)
def tailor_application(req: TailorRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first()
    
    # Prepare candidate structured data
    candidate_data = {
        "name": current_user.full_name,
        "email": current_user.email,
        "phone": profile.phone if profile else "+91 6306211105",
        "location": profile.location if profile else "India",
        "headline": profile.headline if profile else "Software Developer",
        "linkedin_url": profile.linkedin_url if profile else "",
        "github_url": profile.github_url if profile else "",
        "skills": json.loads(profile.skills_json) if (profile and profile.skills_json) else ["Node.js", "Express", "Python", "SQL", "Redis"]
    }

    company = req.company_name or "Target Company"
    role = req.role_title or "Backend Software Engineer"
    provider = req.provider or current_user.preferred_ai or "gemini"

    # API key selection
    api_key = current_user.gemini_api_key if provider == "gemini" else current_user.groq_api_key
    if not api_key:
        api_key = os.getenv("GEMINI_API_KEY") if provider == "gemini" else os.getenv("GROQ_API_KEY")

    # Generate complete application package
    result = AIService.generate_tailored_package(
        candidate_data=candidate_data,
        job_description=req.job_description,
        company_name=company,
        role_title=role,
        api_key=api_key,
        provider=provider
    )

    # Save to Application Tracker automatically
    app_entry = Application(
        user_id=current_user.id,
        company=company,
        role=role,
        status="drafted",
        fit_score=result["fit_score"],
        job_url=req.job_url,
        notes=f"AI Fit: {result['fit_summary']}"
    )
    db.add(app_entry)
    db.commit()
    db.refresh(app_entry)

    # Save generated documents
    doc_cv = GeneratedDocument(
        user_id=current_user.id,
        application_id=app_entry.id,
        company=company,
        role=role,
        doc_type="cv",
        content_text=result["tailored_cv_text"],
        latex_text=result["tailored_cv_latex"]
    )
    doc_cl = GeneratedDocument(
        user_id=current_user.id,
        application_id=app_entry.id,
        company=company,
        role=role,
        doc_type="cover_letter",
        content_text=result["tailored_cover_letter"]
    )
    doc_dm = GeneratedDocument(
        user_id=current_user.id,
        application_id=app_entry.id,
        company=company,
        role=role,
        doc_type="outreach_dm",
        content_text=f"LINKEDIN DM:\n{result['outreach_linkedin_dm']}\n\nCOLD EMAIL:\n{result['outreach_cold_email']}"
    )
    db.add_all([doc_cv, doc_cl, doc_dm])
    db.commit()

    result["application_id"] = app_entry.id
    return result

# ==========================================
# JOB RADAR (Auto Job Discovery)
# ==========================================
@app.get("/api/radar/jobs")
def get_radar_jobs(query: str = "backend", limit: int = 12):
    return JobService.fetch_radar_jobs(query=query, limit=limit)

# ==========================================
# APPLICATIONS PIPELINE (Kanban & Table)
# ==========================================
@app.get("/api/applications", response_model=List[ApplicationOut])
def list_applications(
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    q = db.query(Application).filter(Application.user_id == current_user.id)
    if status and status != "all":
        q = q.filter(Application.status == status)
    return q.order_by(Application.updated_at.desc()).all()

@app.post("/api/applications", response_model=ApplicationOut)
def create_application(app_data: ApplicationCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    new_app = Application(
        user_id=current_user.id,
        company=app_data.company,
        role=app_data.role,
        status=app_data.status or "discovered",
        fit_score=app_data.fit_score or 0,
        contact_name=app_data.contact_name,
        contact_channel=app_data.contact_channel,
        job_url=app_data.job_url,
        notes=app_data.notes
    )
    db.add(new_app)
    db.commit()
    db.refresh(new_app)
    return new_app

@app.put("/api/applications/{app_id}", response_model=ApplicationOut)
def update_application(app_id: int, update_data: ApplicationUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    app_entry = db.query(Application).filter(Application.id == app_id, Application.user_id == current_user.id).first()
    if not app_entry:
        raise HTTPException(status_code=404, detail="Application not found")
    
    for field, val in update_data.dict(exclude_unset=True).items():
        setattr(app_entry, field, val)
    
    app_entry.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(app_entry)
    return app_entry

@app.delete("/api/applications/{app_id}")
def delete_application(app_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    app_entry = db.query(Application).filter(Application.id == app_id, Application.user_id == current_user.id).first()
    if not app_entry:
        raise HTTPException(status_code=404, detail="Application not found")
    db.delete(app_entry)
    db.commit()
    return {"status": "deleted"}

# ==========================================
# DOCUMENT VAULT
# ==========================================
@app.get("/api/documents", response_model=List[DocumentOut])
def list_documents(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(GeneratedDocument).filter(GeneratedDocument.user_id == current_user.id).order_by(GeneratedDocument.created_at.desc()).all()

@app.get("/api/documents/{doc_id}")
def get_document(doc_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    doc = db.query(GeneratedDocument).filter(GeneratedDocument.id == doc_id, GeneratedDocument.user_id == current_user.id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc

# ==========================================
# DASHBOARD FUNNEL STATS
# ==========================================
@app.get("/api/stats", response_model=StatsResponse)
def get_stats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    apps = db.query(Application).filter(Application.user_id == current_user.id).all()
    status_counts = {"discovered": 0, "drafted": 0, "applied": 0, "interview": 0, "offer": 0, "rejected": 0}
    scores = []
    for a in apps:
        status_counts[a.status] = status_counts.get(a.status, 0) + 1
        if a.fit_score:
            scores.append(a.fit_score)
    
    total_docs = db.query(GeneratedDocument).filter(GeneratedDocument.user_id == current_user.id).count()
    avg_score = round(sum(scores) / len(scores), 1) if scores else 0.0

    return StatsResponse(
        total_applications=len(apps),
        status_counts=status_counts,
        avg_fit_score=avg_score,
        total_documents=total_docs
    )

# ==========================================
# SPA ROOT SERVING
# ==========================================
@app.get("/")
def serve_index():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))
