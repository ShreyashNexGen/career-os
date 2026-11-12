import os
import json
from datetime import datetime, date
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, PlainTextResponse
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

from .database import engine, Base, get_db
from .models import User, CandidateProfile, JobPosting, Application, GeneratedDocument, LearningProgress, DailyMomentum
from .auth import hash_password, verify_password, create_access_token, get_current_user
from .schemas import (
    UserRegister, UserLogin, UserOut, UserKeysUpdate,
    ProfileUpdate, ProfileOut,
    TailorRequest, TailorResponse,
    ApplicationCreate, ApplicationUpdate, ApplicationOut,
    DocumentOut, StatsResponse,
    LearningProgressUpdate, DSATutorRequest, SystemDesignReviewRequest,
    ScreeningAnswerRequest, MockGrillRequest, MomentumIncrementRequest
)
from .services.ai_service import AIService
from .services.job_service import JobService
from .data.dsa_200 import DSA_200, DSA_PATTERNS
from .data.system_design import BUILDING_BLOCKS, CASE_STUDIES
from .data.core_cs import CORE_CS_TOPICS

# Initialize DB tables & perform safe additive column migrations
Base.metadata.create_all(bind=engine)
try:
    cols = [c["name"] for c in inspect(engine).get_columns("applications")]
    if "jd_text" not in cols:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE applications ADD COLUMN jd_text TEXT"))
except Exception as _mig_err:
    print(f"[DB Migration Notice] {_mig_err}")


def _bump_momentum(db: Session, user_id: int, metric: str, delta: int = 1):
    today = date.today().isoformat()
    row = db.query(DailyMomentum).filter(DailyMomentum.user_id == user_id, DailyMomentum.date_str == today).first()
    if not row:
        row = DailyMomentum(user_id=user_id, date_str=today, apps_count=0, dsa_count=0, design_count=0)
        db.add(row)
        db.flush()
    if metric == "apps":
        row.apps_count = max(0, (row.apps_count or 0) + delta)
    elif metric == "dsa":
        row.dsa_count = max(0, (row.dsa_count or 0) + delta)
    elif metric == "design":
        row.design_count = max(0, (row.design_count or 0) + delta)
    db.commit()
    return row

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
        db.refresh(app1)

        # Pre-seed tailored documents for ViralMe
        candidate_summary = "Backend-focused Software Engineer with 2+ years of production experience building 250+ RESTful APIs and scalable microservices across Node.js, Express, and Python. Proven track record in database query optimization (35% latency drop), Redis caching, and 99.9% uptime SLA. Elite problem solver ranked Top 28th globally on GeeksforGeeks."
        viralme_cv = AIService._build_text_cv({"name": "Shreyash Shukla", "phone": "+91 6306211105", "email": "shreyashshukla7398554573@gmail.com", "location": "Noida, India"}, candidate_summary)
        viralme_latex = AIService._build_latex_cv({"name": "Shreyash Shukla"}, candidate_summary, "ViralMe", "Founding Backend Engineer")
        viralme_html = AIService._build_html_cv({"name": "Shreyash Shukla"}, candidate_summary, "ViralMe", "Founding Backend Engineer")
        viralme_prep = AIService._build_interview_prep({"name": "Shreyash Shukla"}, "ViralMe", "Founding Backend Engineer", ["Node.js", "Express", "TypeScript", "SQL", "Redis"])

        db.add_all([
            GeneratedDocument(
                user_id=shreyash.id,
                application_id=app1.id,
                company="ViralMe",
                role="Founding Backend & Full Stack Engineer",
                doc_type="cv",
                content_text=viralme_cv,
                latex_text=viralme_latex,
                html_text=viralme_html
            ),
            GeneratedDocument(
                user_id=shreyash.id,
                application_id=app1.id,
                company="ViralMe",
                role="Founding Backend & Full Stack Engineer",
                doc_type="interview_prep",
                content_text=json.dumps(viralme_prep)
            )
        ])
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
    g_key, q_key = AIService.resolve_keys(current_user.gemini_api_key, current_user.groq_api_key)
    return UserOut(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        preferred_ai=current_user.preferred_ai,
        has_gemini_key=bool(g_key),
        has_groq_key=bool(q_key),
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
    provider = req.provider or current_user.preferred_ai or "groq"

    g_key, q_key = AIService.resolve_keys(current_user.gemini_api_key, current_user.groq_api_key)

    # Generate complete application package with multi-provider failover
    result = AIService.generate_tailored_package(
        candidate_data=candidate_data,
        job_description=req.job_description,
        company_name=company,
        role_title=role,
        provider=provider,
        gemini_api_key=g_key,
        groq_api_key=q_key
    )

    # Save to Application Tracker automatically
    app_entry = Application(
        user_id=current_user.id,
        company=company,
        role=role,
        status="drafted",
        fit_score=result["fit_score"],
        job_url=req.job_url,
        jd_text=req.job_description,
        notes=f"AI Fit: {result['fit_summary']}"
    )
    db.add(app_entry)
    db.commit()
    db.refresh(app_entry)
    _bump_momentum(db, current_user.id, "apps", 1)

    # Save generated documents
    doc_cv = GeneratedDocument(
        user_id=current_user.id,
        application_id=app_entry.id,
        company=company,
        role=role,
        doc_type="cv",
        content_text=result["tailored_cv_text"],
        latex_text=result["tailored_cv_latex"],
        html_text=result.get("tailored_cv_html")
    )
    doc_cl = GeneratedDocument(
        user_id=current_user.id,
        application_id=app_entry.id,
        company=company,
        role=role,
        doc_type="cover_letter",
        content_text=result["tailored_cover_letter"]
    )
    
    outreach_bundle = (
        f"--- LINKEDIN CONNECTION NOTE (<280 CHARS) ---\n{result.get('outreach_connection_note', '')}\n\n"
        f"--- LINKEDIN INMAIL / FULL DM ---\n{result.get('outreach_linkedin_dm', '')}\n\n"
        f"--- COLD EMAIL ---\n{result.get('outreach_cold_email', '')}\n\n"
        f"--- DAY 4 FOLLOW-UP BUMP ---\n{result.get('outreach_followup_1', '')}\n\n"
        f"--- DAY 8 VALUE-ADD FOLLOW-UP ---\n{result.get('outreach_followup_2', '')}"
    )
    doc_dm = GeneratedDocument(
        user_id=current_user.id,
        application_id=app_entry.id,
        company=company,
        role=role,
        doc_type="outreach_dm",
        content_text=outreach_bundle
    )

    doc_prep = GeneratedDocument(
        user_id=current_user.id,
        application_id=app_entry.id,
        company=company,
        role=role,
        doc_type="interview_prep",
        content_text=json.dumps(result.get("interview_prep", {}))
    )

    db.add_all([doc_cv, doc_cl, doc_dm, doc_prep])
    db.commit()

    result["application_id"] = app_entry.id
    return result

# ==========================================
# JOB RADAR (Auto Job Discovery)
# ==========================================
@app.get("/api/radar/jobs")
def get_radar_jobs(
    query: str = "all",
    location: str = "all",
    role_type: str = "all",
    company_type: str = "all",
    salary_range: str = "all",
    limit: int = 200
):
    return JobService.fetch_radar_jobs(
        query=query,
        location=location,
        role_type=role_type,
        company_type=company_type,
        salary_range=salary_range,
        limit=limit
    )

# ==========================================
# INSTANT INTERVIEW PREP GENERATOR
# ==========================================
@app.get("/api/prep/instant")
def get_instant_interview_prep(company: str = "ViralMe", role: str = "Backend Software Engineer"):
    return AIService.get_instant_interview_prep(company=company, role=role)

# ==========================================
# SALARY BENCHMARK CALCULATOR
# ==========================================
@app.post("/api/salary-benchmark")
def get_salary_benchmark(payload: dict):
    role = payload.get("role", "Backend Software Engineer")
    exp = float(payload.get("experience_years", 2.0))
    loc = payload.get("location", "Bengaluru")
    tier = payload.get("company_tier", "tier1")
    return AIService.calculate_salary_benchmark(role=role, experience_years=exp, location=loc, company_tier=tier)

# ==========================================
# APPLICATION INTERVIEW PREP RETRIEVAL
# ==========================================
@app.get("/api/applications/{app_id}/prep")
def get_application_prep(app_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    app_entry = db.query(Application).filter(Application.id == app_id, Application.user_id == current_user.id).first()
    if not app_entry:
        raise HTTPException(status_code=404, detail="Application not found")

    # Look for existing interview prep doc
    prep_doc = db.query(GeneratedDocument).filter(
        GeneratedDocument.application_id == app_id,
        GeneratedDocument.doc_type == "interview_prep"
    ).first()

    if prep_doc:
        try:
            return json.loads(prep_doc.content_text)
        except Exception:
            pass

    # Generate on the fly
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first()
    candidate_data = {
        "name": current_user.full_name,
        "email": current_user.email,
        "phone": profile.phone if profile else "+91 6306211105",
        "skills": json.loads(profile.skills_json) if (profile and profile.skills_json) else ["Node.js", "Express", "Python", "SQL", "Redis"]
    }
    prep = AIService._build_interview_prep(candidate_data, app_entry.company, app_entry.role, ["Node.js", "SQL", "Redis"])

    # Cache as document
    new_doc = GeneratedDocument(
        user_id=current_user.id,
        application_id=app_entry.id,
        company=app_entry.company,
        role=app_entry.role,
        doc_type="interview_prep",
        content_text=json.dumps(prep)
    )
    db.add(new_doc)
    db.commit()
    return prep

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
        jd_text=app_data.jd_text,
        notes=app_data.notes
    )
    db.add(new_app)
    db.commit()
    db.refresh(new_app)
    if new_app.status == "applied":
        _bump_momentum(db, current_user.id, "apps", 1)
    return new_app

@app.put("/api/applications/{app_id}", response_model=ApplicationOut)
def update_application(app_id: int, update_data: ApplicationUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    app_entry = db.query(Application).filter(Application.id == app_id, Application.user_id == current_user.id).first()
    if not app_entry:
        raise HTTPException(status_code=404, detail="Application not found")
    
    prev_status = app_entry.status
    for field, val in update_data.dict(exclude_unset=True).items():
        setattr(app_entry, field, val)
    
    app_entry.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(app_entry)
    if prev_status != "applied" and app_entry.status == "applied":
        _bump_momentum(db, current_user.id, "apps", 1)
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
# TOP 200 DSA HUB & LEARNING PROGRESS
# ==========================================
@app.get("/api/dsa")
def get_dsa_sheet(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.query(LearningProgress).filter(
        LearningProgress.user_id == current_user.id,
        LearningProgress.category == "dsa"
    ).all()
    prog_map = {r.item_id: {"status": r.status, "notes": r.notes or ""} for r in rows}

    problems = []
    solved_cnt = 0
    revisit_cnt = 0
    for item in DSA_200:
        st_info = prog_map.get(item["id"], {"status": "todo", "notes": ""})
        if st_info["status"] == "solved":
            solved_cnt += 1
        elif st_info["status"] == "revisit":
            revisit_cnt += 1
        enriched = dict(item)
        enriched["status"] = st_info["status"]
        enriched["notes"] = st_info["notes"]
        problems.append(enriched)

    return {
        "patterns": DSA_PATTERNS,
        "problems": problems,
        "stats": {"total": len(DSA_200), "solved": solved_cnt, "revisit": revisit_cnt}
    }

@app.post("/api/learning/progress")
def update_learning_progress(
    payload: LearningProgressUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    row = db.query(LearningProgress).filter(
        LearningProgress.user_id == current_user.id,
        LearningProgress.category == payload.category,
        LearningProgress.item_id == payload.item_id
    ).first()

    prev_status = row.status if row else "todo"
    if not row:
        row = LearningProgress(
            user_id=current_user.id,
            category=payload.category,
            item_id=payload.item_id,
            status=payload.status or "todo",
            notes=payload.notes
        )
        db.add(row)
    else:
        if payload.status is not None:
            row.status = payload.status
        if payload.notes is not None:
            row.notes = payload.notes
        row.updated_at = datetime.utcnow()

    db.commit()

    if prev_status != "solved" and payload.status == "solved":
        if payload.category == "dsa":
            _bump_momentum(db, current_user.id, "dsa", 1)
        elif payload.category in ("sysdesign", "corecs"):
            _bump_momentum(db, current_user.id, "design", 1)

    return {"status": "ok", "item_id": payload.item_id, "new_status": row.status}

@app.post("/api/dsa/ai-tutor")
def run_dsa_ai_tutor(req: DSATutorRequest, current_user: User = Depends(get_current_user)):
    g_key, q_key = AIService.resolve_keys(current_user.gemini_api_key, current_user.groq_api_key)
    preferred = current_user.preferred_ai if current_user.preferred_ai in ("groq", "gemini") else "groq"
    return AIService.ai_dsa_tutor(
        title=req.title,
        pattern=req.pattern,
        language=req.language,
        mode=req.mode,
        user_input=req.user_input or "",
        preferred=preferred,
        gemini_key=g_key,
        groq_key=q_key
    )

# ==========================================
# SYSTEM DESIGN ACADEMY & CORE CS
# ==========================================
@app.get("/api/sysdesign")
def get_system_design_hub(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.query(LearningProgress).filter(
        LearningProgress.user_id == current_user.id,
        LearningProgress.category == "sysdesign"
    ).all()
    prog_map = {r.item_id: r.status for r in rows}
    return {
        "building_blocks": BUILDING_BLOCKS,
        "case_studies": CASE_STUDIES,
        "progress": prog_map
    }

@app.post("/api/sysdesign/ai-review")
def run_sysdesign_ai_review(req: SystemDesignReviewRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    g_key, q_key = AIService.resolve_keys(current_user.gemini_api_key, current_user.groq_api_key)
    preferred = current_user.preferred_ai if current_user.preferred_ai in ("groq", "gemini") else "groq"
    _bump_momentum(db, current_user.id, "design", 1)
    return AIService.ai_system_design_review(
        case_title=req.case_title,
        user_design=req.user_design,
        preferred=preferred,
        gemini_key=g_key,
        groq_key=q_key
    )

@app.get("/api/corecs")
def get_core_cs_topics():
    return {"topics": CORE_CS_TOPICS}

# ==========================================
# EASY APPLY SCREENING HELPER & MOCK GRILL
# ==========================================
@app.post("/api/ai/screening-answer")
def generate_screening_answer(req: ScreeningAnswerRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first()
    candidate_data = {
        "name": current_user.full_name,
        "headline": profile.headline if profile else "Backend / Full Stack Engineer"
    }
    g_key, q_key = AIService.resolve_keys(current_user.gemini_api_key, current_user.groq_api_key)
    preferred = current_user.preferred_ai if current_user.preferred_ai in ("groq", "gemini") else "groq"
    return AIService.ai_screening_answer(
        company=req.company,
        role=req.role,
        question=req.question,
        jd_text=req.jd_text or "",
        candidate_data=candidate_data,
        preferred=preferred,
        gemini_key=g_key,
        groq_key=q_key
    )

@app.post("/api/ai/mock-grill")
def run_mock_grill(req: MockGrillRequest, current_user: User = Depends(get_current_user)):
    g_key, q_key = AIService.resolve_keys(current_user.gemini_api_key, current_user.groq_api_key)
    preferred = current_user.preferred_ai if current_user.preferred_ai in ("groq", "gemini") else "groq"
    return AIService.ai_mock_grill(
        company=req.company,
        role=req.role,
        question=req.question,
        user_answer=req.user_answer,
        focus_area=req.focus_area,
        preferred=preferred,
        gemini_key=g_key,
        groq_key=q_key
    )

# ==========================================
# DAILY MOMENTUM TRACKER
# ==========================================
@app.get("/api/momentum")
def get_today_momentum(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    today = date.today().isoformat()
    row = db.query(DailyMomentum).filter(DailyMomentum.user_id == current_user.id, DailyMomentum.date_str == today).first()
    if not row:
        return {"date": today, "apps_count": 0, "dsa_count": 0, "design_count": 0}
    return {
        "date": today,
        "apps_count": row.apps_count or 0,
        "dsa_count": row.dsa_count or 0,
        "design_count": row.design_count or 0
    }

@app.post("/api/momentum")
def increment_momentum(req: MomentumIncrementRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    row = _bump_momentum(db, current_user.id, req.metric, req.delta)
    return {
        "date": row.date_str,
        "apps_count": row.apps_count or 0,
        "dsa_count": row.dsa_count or 0,
        "design_count": row.design_count or 0
    }

# ==========================================
# SPA ROOT SERVING
# ==========================================
@app.get("/")
def serve_index():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))
