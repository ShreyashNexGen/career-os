# CareerOS — AI-Powered Job Search & Application Platform (SaaS MVP)

An end-to-end full-stack SaaS platform built for high-conversion technical job searches. Designed for software engineers, CareerOS automates job discovery, evaluates ATS fit, tailors resumes and cover letters using **completely free AI models (no credit card required)**, and tracks active application pipelines on a real-time Kanban board.

---

## 🚀 Quick Start (Running Locally)

### 1. Start the Platform
In PowerShell or terminal:
```bash
cd C:\Users\dell\Desktop\Personal-Automation\career-os
python run.py
```

### 2. Open in Your Browser
- **Web Application Dashboard:** [http://localhost:8000](http://localhost:8000)
- **Interactive Swagger API Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## ⚡ Core Features

1. **Multi-User SaaS Architecture:**
   - Isolated user workspaces with JWT authentication.
   - Pre-seeded with **Shreyash Shukla** (Primary Master Account) and **Alex Friend** (Friend Demo Account).
   - Easily invite friends or add new users.

2. **1-Click AI Tailoring Engine:**
   - Paste any job posting link or description.
   - Computes ATS match score (0–100%) and highlights matched vs. missing skills.
   - Injects your verified production metrics (250+ APIs, 35% latency drop, 99.9% uptime, GFG Rank 28).
   - Generates:
     - Tailored ATS Resume (Plain text + ModernCV LaTeX).
     - Tailored 1-page Cover Letter.
     - Personalized Cold Outreach DMs for LinkedIn and Email.

3. **Free AI Integration (Zero Credit Card Required):**
   - **Google Gemini 1.5 Flash:** 100% free via Google AI Studio (15 RPM, no card needed).
   - **Groq Cloud:** Ultra-fast inference running Llama 3.3 70B & DeepSeek R1 for free.
   - **Smart Offline Engine:** Built-in heuristic fallback so the app works 100% out of the box even without API keys!

4. **Automated Job Radar:**
   - Aggregates live tech postings from public developer APIs (RemoteOK, Jobicy) and curated engineering pipelines.
   - One-click "Tailor & Apply" to immediately draft documents for any discovered role.

5. **Pipeline & Kanban Tracker:**
   - Visual board: `Discovered` → `Drafted` → `Applied` → `Interview` → `Offer`.
   - Real-time status updates and funnel conversion metrics.

6. **Document Vault:**
   - Central archive storing every tailored CV, cover letter, and outreach draft.
   - One-click preview and download as `.tex` or `.txt`.

---

## 🛠️ Tech Stack

- **Backend:** Python 3.13, FastAPI (Async REST APIs, Auto OpenAPI/Swagger)
- **Database:** SQLite with SQLAlchemy ORM (Multi-tenant schema)
- **Authentication:** JWT with PBKDF2-HMAC password encryption
- **Frontend:** Single Page Application (Tailwind CSS, FontAwesome, Vanilla JS)
- **AI Engine:** Google Gemini REST API / Groq Cloud REST API / Smart Local Heuristics
