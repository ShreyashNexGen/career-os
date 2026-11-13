import os
import json
import re
import requests
from typing import Dict, Any, List, Optional

class AIService:

    @staticmethod
    def resolve_keys(gemini_key: Optional[str] = None, groq_key: Optional[str] = None):
        """Resolve per-user keys with safe environment variable fallbacks."""
        g_key = (gemini_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_GENERATIVE_AI_API_KEY") or "").strip()
        q_key = (groq_key or os.getenv("GROQ_API_KEY") or "").strip()
        return g_key or None, q_key or None

    @staticmethod
    def call_gemini(prompt: str, api_key: str) -> str:
        """Call Google Gemini API via standard REST, trying stable Flash models."""
        models_to_try = ["gemini-2.5-flash", "gemini-3.5-flash-lite"]
        last_err = None
        for model_id in models_to_try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent?key={api_key}"
            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "temperature": 0.3,
                    "maxOutputTokens": 6000
                }
            }
            headers = {"Content-Type": "application/json"}
            resp = requests.post(url, headers=headers, json=payload, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                candidates = data.get("candidates", [])
                if candidates and "content" in candidates[0]:
                    parts = candidates[0]["content"].get("parts", [])
                    if parts:
                        return parts[0].get("text", "")
            last_err = f"Gemini API error ({resp.status_code}): {resp.text[:300]}"
            if resp.status_code in (400, 401, 403):
                break
        raise Exception(last_err or "Gemini API failed")

    @staticmethod
    def call_groq(prompt: str, api_key: str) -> str:
        """Call Groq Cloud API directly via OpenAI-compatible endpoint."""
        url = "https://api.groq.com/openai/v1/chat/completions"
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": "You are an elite technical recruiter and Principal Software Architect."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 6000
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        resp = requests.post(url, headers=headers, json=payload, timeout=35)
        if resp.status_code != 200:
            raise Exception(f"Groq API error ({resp.status_code}): {resp.text[:300]}")
        data = resp.json()
        choices = data.get("choices", [])
        if choices:
            return choices[0]["message"]["content"]
        return ""

    @classmethod
    def execute_llm_prompt(
        cls,
        prompt: str,
        preferred: str = "groq",
        gemini_key: Optional[str] = None,
        groq_key: Optional[str] = None
    ) -> tuple[Optional[str], str]:
        """Try preferred AI provider, automatically failing over to backup provider if configured."""
        if preferred == "offline":
            return None, "offline"

        g_key, q_key = cls.resolve_keys(gemini_key, groq_key)
        order = [("groq", q_key), ("gemini", g_key)] if preferred == "groq" else [("gemini", g_key), ("groq", q_key)]

        for prov, key in order:
            if not key:
                continue
            try:
                text = cls.call_groq(prompt, key) if prov == "groq" else cls.call_gemini(prompt, key)
                if text and text.strip():
                    return text.strip(), prov
            except Exception as e:
                print(f"[AIService Warning] {prov} failed ({str(e)[:180]}). Trying fallback...")
                continue

        return None, "offline"

    @classmethod
    def generate_tailored_package(
        cls,
        candidate_data: Dict[str, Any],
        job_description: str,
        company_name: str,
        role_title: str,
        api_key: str = None,
        provider: str = "gemini",
        gemini_api_key: Optional[str] = None,
        groq_api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Orchestrates AI analysis and document generation with multi-provider failover.
        Falls back to our master algorithmic engine if no API key succeeds.
        """
        if provider != "offline":
            g_key = gemini_api_key or (api_key if provider == "gemini" else None)
            q_key = groq_api_key or (api_key if provider == "groq" else None)
            try:
                return cls._llm_tailor(candidate_data, job_description, company_name, role_title, provider, g_key, q_key)
            except Exception as e:
                print(f"[AIService Warning] LLM tailor fallback triggered ({str(e)[:180]}).")

        return cls._rule_based_tailor(candidate_data, job_description, company_name, role_title)

    @classmethod
    def _llm_tailor(
        cls,
        candidate: Dict[str, Any],
        jd: str,
        company: str,
        role: str,
        provider: str,
        gemini_key: Optional[str] = None,
        groq_key: Optional[str] = None
    ) -> Dict[str, Any]:
        prompt = f"""
You are an elite Silicon Valley / Indian Tech technical recruiter and Principal Systems Architect.
Candidate Profile:
{json.dumps(candidate, indent=2)}

Target Role: {role} at {company}
Job Description:
{jd}

TASK:
Perform a deep ATS alignment and interview strategy.
Return a STRICT valid JSON object with the following exact keys:
{{
  "fit_score": <integer from 0 to 100>,
  "fit_summary": "<2-3 punchy sentences highlighting direct technical overlaps and impact>",
  "matching_skills": ["<skill 1>", "<skill 2>", ...],
  "missing_skills": ["<missing skill or learnable gap>", ...],
  "tailored_profile_summary": "<3-4 sentence impactful summary emphasizing 250+ APIs, 35% latency cut, and GFG Rank 28>",
  "tailored_cover_letter": "<Full 1-page forward-looking cover letter addressing {company}'s specific engineering problems. No generic filler, no em-dashes>",
  "outreach_connection_note": "<Crisp LinkedIn connection note under 280 characters with direct value hook>",
  "outreach_linkedin_dm": "<3-paragraph value-first LinkedIn InMail pitch with proof of work>",
  "outreach_cold_email_subject": "<High-open-rate subject line with candidate name and key metrics>",
  "outreach_cold_email": "<Full cold email body with bullet proof-points>",
  "outreach_followup_1": "<Polite Day 4 bump message with specific question on company tech>",
  "outreach_followup_2": "<Day 8 value-add follow-up proposing architecture approach>",
  "interview_top_questions": [
    {{"question": "<Technical question likely asked for this stack>", "answer": "<Comprehensive expert model answer>"}}
  ],
  "interview_system_design": "<Complete system design architectural blueprint for {company}'s domain>"
}}
Return ONLY raw JSON, without markdown formatting or code fences.
"""
        raw_output, _used = cls.execute_llm_prompt(prompt, preferred=provider, gemini_key=gemini_key, groq_key=groq_key)
        if not raw_output:
            raise Exception("All configured LLM providers failed or returned empty.")
        raw_output = re.sub(r"^```json\s*", "", raw_output.strip())
        raw_output = re.sub(r"^```\s*", "", raw_output)
        raw_output = re.sub(r"\s*```$", "", raw_output)

        data = json.loads(raw_output)

        summary = data.get("tailored_profile_summary", "")
        latex_cv = cls._build_latex_cv(candidate, summary, company, role)
        cv_text = cls._build_text_cv(candidate, summary)
        html_cv = cls._build_html_cv(candidate, summary, company, role)

        # Merge with master STAR stories and reverse questions
        matched = data.get("matching_skills", ["Node.js", "Express", "SQL", "Redis"])
        interview_prep = cls._build_interview_prep(candidate, company, role, matched)
        if data.get("interview_top_questions"):
            interview_prep["questions"] = data["interview_top_questions"][:10]
        if data.get("interview_system_design"):
            interview_prep["system_design"] = data["interview_system_design"]

        cold_email = data.get("outreach_cold_email", "")
        if "Subject:" not in cold_email and data.get("outreach_cold_email_subject"):
            cold_email = f"Subject: {data['outreach_cold_email_subject']}\n\n{cold_email}"

        return {
            "company_name": company,
            "role_title": role,
            "fit_score": int(data.get("fit_score", 92)),
            "fit_summary": data.get("fit_summary", "Strong technical match based on production backend experience."),
            "matching_skills": matched,
            "missing_skills": data.get("missing_skills", []),
            "tailored_cv_text": cv_text,
            "tailored_cv_latex": latex_cv,
            "tailored_cv_html": html_cv,
            "tailored_cover_letter": data.get("tailored_cover_letter", ""),
            "outreach_linkedin_dm": data.get("outreach_linkedin_dm", ""),
            "outreach_connection_note": data.get("outreach_connection_note", f"Hi! Saw {company}'s {role} opening. I build 250+ production APIs, cut SQL latency by 35% with Redis, and rank #28 on GFG. Would love to connect!"),
            "outreach_cold_email": cold_email,
            "outreach_followup_1": data.get("outreach_followup_1", cls._default_followup_1(company, role, candidate)),
            "outreach_followup_2": data.get("outreach_followup_2", cls._default_followup_2(company, role, candidate)),
            "interview_prep": interview_prep
        }

    @classmethod
    def _rule_based_tailor(cls, candidate: Dict[str, Any], jd: str, company: str, role: str) -> Dict[str, Any]:
        """Master rule-based generation with verified production metrics."""
        jd_lower = jd.lower()
        skills = candidate.get("skills", ["Node.js", "Express", "Python", "SQL", "Redis", "Docker", "REST APIs"])

        matched = [s for s in skills if s.lower() in jd_lower]
        if not matched:
            matched = ["Node.js", "Express", "SQL", "Redis", "Microservices"]

        fit_score = min(96, 78 + len(matched) * 3)

        summary = (
            f"Backend-focused Software Engineer with 2+ years of production experience architecting 250+ RESTful APIs "
            f"and scalable microservices in Node.js, Express, and Python. Proven track record in database performance optimization "
            f"(35% query latency reduction), Redis caching, and 99.9% uptime SLA. Elite problem solver ranked Top 28th globally "
            f"out of 8,000+ competitors on GeeksforGeeks (800+ solved) and KAVACH national hackathon finalist, applying high-velocity "
            f"AI engineering workflows to ship reliable systems for {company}."
        )

        letter = f"""Dear Hiring Team at {company},

I am writing to express my strong interest in the {role} position at {company}. Having engineered over 250 production RESTful APIs and low-latency data pipelines handling high-concurrency workloads, I am eager to contribute to your engineering infrastructure.

In my current role at NexGen, I designed and maintained core multi-tenant enterprise backend systems using Node.js, Express, and Flask over MySQL and MongoDB. A key highlight was refactoring database query execution plans, stored procedures, and B-Tree indexes, achieving a 35% latency drop on bulk transactions, paired with Redis caching. Additionally, I built an automated Python reconciliation engine that cut manual accounting overhead by 70%.

What excites me about {company} is the opportunity to solve real architectural challenges with high autonomy. My foundation in Data Structures and Algorithms (ranked 28th out of 8,000+ globally on GeeksforGeeks) allows me to reason rigorously about edge cases, system bottlenecks, and clean API abstractions.

I welcome the opportunity to discuss how my backend and systems engineering background can support {company}'s roadmap.

Kind regards,
{candidate.get('name', 'Shreyash Shukla')}
{candidate.get('phone', '+91 6306211105')} | {candidate.get('email', 'shreyashshukla7398554573@gmail.com')}
"""

        connection_note = f"Hi! Saw {company}'s {role} opening. I build 250+ production APIs, cut SQL latency by 35% with Redis, and rank #28 on GFG. Would love to connect!"

        linkedin_dm = f"""Hi Hiring Team / Engineering Lead at {company},

I noticed the {role} opening at {company} and wanted to reach out directly.

I'm a backend and systems software engineer (Node.js, Express, Python, SQL, Redis) with 2+ years of production experience building 250+ RESTful APIs and cutting transaction latency by 35% across high-concurrency enterprise services. I also solved 800+ DSA problems (Ranked #28 globally on GeeksforGeeks) and work with high velocity using modern AI developer tooling.

Would love to contribute to {company}'s engineering foundation. Open to onsite or remote. Would you be open to a brief chat this week?
"""

        cold_email = f"""Subject: {role} Application — {candidate.get('name', 'Shreyash Shukla')} (Node.js, 250+ APIs, GFG #28)

Dear Hiring Team at {company},

I am writing to apply for the {role} role at {company}.

A brief snapshot of what I bring to your engineering team:
• 250+ Production REST APIs architected across Node.js, Express, and Flask with 99.9% uptime SLA.
• Database Performance Tuning: Reduced high-concurrency SQL transaction latency by 35% through execution plan analysis and index optimization, backed by Redis caching.
• High-Velocity Delivery: Shipped 6+ production enterprise systems in my first year at NexGen.
• Algorithmic Pedigree: Ranked 28th globally among 8,000+ competitors on GeeksforGeeks (800+ solved).

My GitHub & Portfolio: {candidate.get('github_url', 'https://github.com/shreyash418')}
Phone: {candidate.get('phone', '+91 6306211105')}

I would welcome the opportunity to discuss how my systems background can help {company} scale.

Best regards,
{candidate.get('name', 'Shreyash Shukla')}
"""

        followup_1 = cls._default_followup_1(company, role, candidate)
        followup_2 = cls._default_followup_2(company, role, candidate)
        interview_prep = cls._build_interview_prep(candidate, company, role, matched)

        latex_cv = cls._build_latex_cv(candidate, summary, company, role)
        cv_text = cls._build_text_cv(candidate, summary)
        html_cv = cls._build_html_cv(candidate, summary, company, role)

        return {
            "company_name": company,
            "role_title": role,
            "fit_score": fit_score,
            "fit_summary": f"Strong alignment on backend architecture, API scalability, and {', '.join(matched[:3])}.",
            "matching_skills": matched,
            "missing_skills": ["Domain-specific proprietary tools"],
            "tailored_cv_text": cv_text,
            "tailored_cv_latex": latex_cv,
            "tailored_cv_html": html_cv,
            "tailored_cover_letter": letter,
            "outreach_linkedin_dm": linkedin_dm,
            "outreach_connection_note": connection_note,
            "outreach_cold_email": cold_email,
            "outreach_followup_1": followup_1,
            "outreach_followup_2": followup_2,
            "interview_prep": interview_prep
        }

    @staticmethod
    def _default_followup_1(company: str, role: str, candidate: Dict[str, Any]) -> str:
        return f"""Subject: Re: {role} Application — {candidate.get('name', 'Shreyash Shukla')}

Hi Team at {company},

Following up on my note from earlier this week regarding the {role} position.

I've been reviewing {company}'s tech milestones and would love to contribute to your backend throughput and database optimization goals. With 2+ years of experience maintaining 250+ production APIs and a Top 28 rank on GeeksforGeeks, I'm confident I can make an immediate impact.

Looking forward to hearing from you.

Best,
{candidate.get('name', 'Shreyash Shukla')}
{candidate.get('phone', '+91 6306211105')}
"""

    @staticmethod
    def _default_followup_2(company: str, role: str, candidate: Dict[str, Any]) -> str:
        return f"""Subject: Quick follow-up & technical thoughts for {company} ({role})

Hi Team at {company},

Hope you're having a great week!

I put together some architectural notes on how I'd approach low-latency caching and automated reconciliation for {company}'s scale. Having tuned SQL execution plans for a 35% latency drop on bulk transactions at NexGen, I'm excited about the challenges you're tackling.

If you have 10 minutes this week, I'd love to share my portfolio and walk through these system design patterns.

Kind regards,
{candidate.get('name', 'Shreyash Shukla')}
"""

    @classmethod
    def get_instant_interview_prep(cls, company: str, role: str) -> Dict[str, Any]:
        candidate = {
            "name": "Shreyash Shukla",
            "phone": "+91 6306211105",
            "email": "shreyashshukla7398554573@gmail.com",
            "location": "Noida, India",
            "github_url": "https://github.com/shreyash418",
            "linkedin_url": "https://linkedin.com/in/shuklashreyash"
        }
        return cls._build_interview_prep(candidate, company, role, ["Node.js", "Express", "Python", "SQL", "Redis", "Microservices", "System Design"])

    @staticmethod
    def _build_interview_prep(candidate: Dict[str, Any], company: str, role: str, matched_skills: List[str]) -> Dict[str, Any]:
        """Generates comprehensive interview prep with questions, STAR stories, system design, and reverse questions."""
        questions = [
            {
                "question": "How does the Node.js Event Loop work, and how do you prevent CPU-intensive tasks from blocking incoming API requests?",
                "answer": "Node.js runs single-threaded on the V8 engine using an event-driven, non-blocking I/O model backed by libuv. The loop has 6 phases: Timers (setTimeout), Pending Callbacks, Idle/Prepare, Poll (incoming I/O), Check (setImmediate), and Close Callbacks. Microtasks (process.nextTick, Promise callbacks) run after each phase before moving to the next. To prevent blocking the main thread on heavy tasks (e.g. data encryption, image processing, or big JSON parsing), we offload work to Worker Threads (worker_threads module), child processes, or asynchronous background queues (BullMQ/Redis/RabbitMQ)."
            },
            {
                "question": "How did you achieve a 35% latency reduction in database transactions? Explain your profiling and indexing strategy.",
                "answer": "At NexGen, bulk transaction endpoints were experiencing high P99 latency. I ran EXPLAIN / execution plan analysis in MS SQL Server and MySQL, identifying frequent table scans and inefficient sort operations. I refactored queries to eliminate Cartesian joins, converted multi-column filters to composite B-Tree indexes matching leftmost prefix rules, and replaced dynamic OR filters with UNION ALL where appropriate. In addition, I introduced Redis caching with a cache-aside pattern for frequently read reference data with short TTLs, reducing database IOPS by over 50% and cutting transaction latency by 35%."
            },
            {
                "question": "How do you design an API rate limiter to protect microservices from abuse?",
                "answer": "I implement a Token-Bucket or Sliding Window Counter algorithm backed by Redis. In a Token-Bucket, each client IP/API key has a Redis key with tokens that regenerate at a constant rate. Using an atomic Redis Lua script (or MULTI/EXEC with INCR and EXPIRE), we decrement the token counter. If tokens reach 0, we immediately return HTTP 429 Too Many Requests with headers Retry-After and X-RateLimit-Remaining. Redis in-memory lookup ensures rate limiting executes with sub-millisecond overhead at the API gateway layer."
            },
            {
                "question": "What is Idempotency and why is it crucial for financial or ERP transactions?",
                "answer": "An idempotent API ensures that making the same request multiple times produces the exact same server state without duplicate side-effects (e.g. charging a card twice or creating duplicate inventory entries). We implement this by requiring clients to send a unique Idempotency-Key in HTTP headers. The server checks Redis or a dedicated database table for the key within an atomic transaction. If found and completed, it returns the cached response; if currently processing, it returns 409 Conflict or waits; if new, it executes the operation and stores the result."
            },
            {
                "question": "How do you handle real-time data streaming and telemetry under high burst loads?",
                "answer": "In my Warehouse Automation project, I built a pipeline from industrial PLC hardware to Flask microservices handling burst data. To guarantee 5-10ms latency and 99.2% accuracy without dropping frames, I decoupled ingestion from consumption using in-memory ring buffers and asynchronous WebSocket event loops. When network jitter occurred, local buffers held packets and re-flushed them on reconnection with monotonic sequence numbers to prevent out-of-order writes."
            },
            {
                "question": "Compare Redis vs Memcached, and explain your cache eviction strategy.",
                "answer": "While Memcached is multi-threaded and purely key-value, Redis offers rich in-memory data structures (Hashes, Sets, Sorted Sets, Streams), persistence (RDB/AOF), and built-in pub/sub. For high-scale web platforms, we configure Redis with 'allkeys-lru' (Least Recently Used) or 'volatile-lru' eviction. To prevent cache stampedes (dog-piling) when popular keys expire, we use probabilistic early expiration (XFetch) or distributed locks (Redlock) so only one worker thread recomputes the database cache while others read the stale value."
            },
            {
                "question": "How do you implement secure Authentication & Authorization across multi-tenant microservices?",
                "answer": "I use an Identity & Access Management (IAM) architecture using stateless JWTs for authentication and Role-Based Access Control (RBAC) for authorization. The API Gateway cryptographically verifies the JWT signature and extracts user claims (tenantId, userId, roles, permissions). Downstream microservices receive trusted correlation headers (e.g., X-User-Id, X-Tenant-Id) without re-querying the auth database. Access tokens have short TTLs (15-60 min) with secure, httpOnly refresh token rotation."
            },
            {
                "question": "Explain database Transaction Isolation Levels and the anomalies they prevent.",
                "answer": "ANSI SQL defines 4 levels: Read Uncommitted (allows dirty reads), Read Committed (prevents dirty reads, allows non-repeatable reads), Repeatable Read (prevents dirty & non-repeatable reads using snapshot reads or row locks, but may allow phantom reads in some engines), and Serializable (strict two-phase locking or multi-version concurrency control, preventing all anomalies at the cost of concurrency). In high-throughput ERP and payments, Read Committed with optimistic locking (version column) provides the optimal balance of consistency and throughput."
            }
        ]

        star_stories = [
            {
                "title": "Automated Reconciliation Engine (70% Manual Effort Eliminated)",
                "situation": "Enterprise clients at NexGen suffered from cross-department ledger discrepancies that required finance teams to spend 15+ hours weekly manually comparing spreadsheets against SQL databases.",
                "task": "Design and build an automated reconciliation microservice to balance ledgers, detect variances, and generate audit-ready reports.",
                "action": "Engineered an automated Python engine scheduled via cron/background workers that ingested bank & ERP data into MS SQL Server, executed set-based reconciliation queries with composite indexing, and flagged anomalies with email alerts.",
                "result": "Cut manual accounting overhead by 70%, reduced reconciliation time from 2 days to under 4 minutes, and maintained zero ledger discrepancy across multi-tenant clients."
            },
            {
                "title": "Real-Time Warehouse Automation Telemetry (5-10ms Latency & 99.2% Accuracy)",
                "situation": "Industrial factory floor PLC machinery experienced packet drops and high communication latency (100ms+) when polling sensory telemetry via standard HTTP.",
                "task": "Build a low-latency telemetry pipeline connecting Siemens S7 / Snap7 PLCs with Flask backend services and a live operator dashboard.",
                "action": "Implemented an asynchronous binary packet decoder with Snap7, engineered local in-memory failover buffering to absorb network drops, and streamed live telemetry via WebSockets.",
                "result": "Delivered sub-10ms response latency, achieved 99.2% ingestion accuracy during burst loads, and decreased machine downtime troubleshooting by 40%."
            },
            {
                "title": "High-Concurrency Database Performance Optimization (35% Latency Reduction)",
                "situation": "High-concurrency bulk transactions in our core ERP platform caused query queueing, locking timeouts, and slow P99 response times on MySQL and MS SQL Server.",
                "task": "Optimize database throughput and eliminate slow queries without expensive infrastructure upgrades.",
                "action": "Analyzed slow-query logs and execution plans, restructured stored procedures, created covering B-Tree indexes matching filter cardinality, and implemented Redis caching for hot master records.",
                "result": "Reduced bulk transaction query latency by 35%, lowered database CPU and IOPS by over 50%, and upheld a 99.9% uptime SLA across all production services."
            }
        ]

        system_design = f"""SYSTEM DESIGN BLUEPRINT: High-Throughput Architecture for {company}

1. HIGH-LEVEL FLOW:
[Clients / Web / Mobile] 
    ↓ HTTPS / WSS
[Cloudflare CDN & Edge DDoS Protection]
    ↓ 
[Reverse Proxy & API Gateway (Node.js / Express)]
    ├── Token-Bucket Rate Limiter (Redis)
    ├── JWT Validation & RBAC Auth Check
    └── Correlation ID Tracing Injection
    ↓ (Internal gRPC / REST)
[Microservices Cluster (Dockerized Node.js / Python)]
    ├── Read Path: Redis Cache Cluster (Sub-5ms response)
    ├── Write Path: Master DB (PostgreSQL / MySQL with ACID compliance)
    └── Async Path: Background Workers (BullMQ / RabbitMQ for heavy jobs & webhooks)
    ↓
[Database Tier: Read/Write Split with Read Replicas]

2. KEY BOTTLENECK MITIGATION:
- Cache Stampede: Use distributed Redlock locks and stale-while-revalidate policies.
- Database Write Scalability: Implement write batching and connection pooling (PgBouncer / HikariCP).
- Idempotency: Enforce unique Idempotency-Key headers for all transactional mutations.
- Observability: Prometheus metrics, Grafana dashboards, and Winston/Pino JSON structured logging.
"""

        reverse_questions = [
            f"What does the P99 latency and daily transaction volume look like across {company}'s core services today?",
            "How does your team handle database schema migrations across zero-downtime deployments?",
            f"What are the biggest architectural bottlenecks {company}'s engineering team is focused on solving this quarter?",
            "How do your engineers leverage modern AI developer tooling (like Claude Code and Cursor) to accelerate shipping velocity?",
            "What does a successful engineer's first 90 days look like on this team?"
        ]

        return {
            "questions": questions,
            "star_stories": star_stories,
            "system_design": system_design,
            "reverse_questions": reverse_questions
        }

    @staticmethod
    def _build_html_cv(candidate: Dict[str, Any], summary: str, company: str, role: str) -> str:
        name = candidate.get("name", "Shreyash Shukla")
        phone = candidate.get("phone", "+91 6306211105")
        email = candidate.get("email", "shreyashshukla7398554573@gmail.com")
        loc = candidate.get("location", "Noida, India (Open to Bengaluru & Remote)")
        linkedin = candidate.get("linkedin_url", "https://linkedin.com/in/shuklashreyash")
        github = candidate.get("github_url", "https://github.com/shreyash418")

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{name} - Resume ({company})</title>
  <style>
    @page {{ size: A4; margin: 12mm 15mm; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      color: #1e293b;
      line-height: 1.45;
      font-size: 11pt;
      margin: 0;
      padding: 20px;
      background: white;
    }}
    .header {{ text-align: center; border-bottom: 2px solid #2563eb; padding-bottom: 8px; margin-bottom: 12px; }}
    .name {{ font-size: 24pt; font-weight: 800; color: #1e3a8a; letter-spacing: -0.5px; margin: 0; }}
    .headline {{ font-size: 11pt; font-weight: 600; color: #2563eb; margin: 4px 0; }}
    .contact {{ font-size: 9.5pt; color: #475569; }}
    .contact a {{ color: #2563eb; text-decoration: none; }}
    .section-title {{
      font-size: 11.5pt;
      font-weight: 700;
      color: #1e3a8a;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      border-bottom: 1px solid #cbd5e1;
      padding-bottom: 2px;
      margin-top: 14px;
      margin-bottom: 6px;
    }}
    .summary-text {{ font-size: 10pt; color: #334155; text-align: justify; margin-bottom: 8px; }}
    .job-header {{ display: flex; justify-content: space-between; font-weight: 700; font-size: 10.5pt; color: #0f172a; margin-top: 6px; }}
    .job-sub {{ display: flex; justify-content: space-between; font-size: 9.5pt; color: #2563eb; font-weight: 600; margin-bottom: 4px; }}
    ul {{ margin: 3px 0 8px 18px; padding: 0; }}
    li {{ font-size: 9.5pt; color: #334155; margin-bottom: 3px; }}
    .skills-grid {{ font-size: 9.5pt; color: #334155; }}
    .skills-grid strong {{ color: #0f172a; }}
    @media print {{
      body {{ padding: 0; }}
      .no-print {{ display: none !important; }}
    }}
  </style>
</head>
<body>
  <div class="header">
    <h1 class="name">{name}</h1>
    <div class="headline">Backend & Systems Software Engineer | Target: {role}</div>
    <div class="contact">
      {loc} &nbsp;|&nbsp; 
      {phone} &nbsp;|&nbsp; 
      <a href="mailto:{email}">{email}</a> &nbsp;|&nbsp; 
      <a href="{linkedin}">LinkedIn</a> &nbsp;|&nbsp; 
      <a href="{github}">GitHub</a> &nbsp;|&nbsp; 
      <a href="https://auth.geeksforgeeks.org/user/shuklashreyash">GFG (Rank 28/8k+)</a>
    </div>
  </div>

  <div class="section-title">Professional Summary</div>
  <div class="summary-text">{summary}</div>

  <div class="section-title">Technical Skills Matrix</div>
  <div class="skills-grid">
    <div><strong>Languages:</strong> C++, Python, JavaScript (ES6+), TypeScript, SQL, HTML5, CSS3</div>
    <div><strong>Backend & APIs:</strong> Node.js, Express.js, Flask, RESTful APIs, Microservices, MVC Architecture, WebSockets, Rate Limiting</div>
    <div><strong>Databases & Caching:</strong> MS SQL Server, MySQL, MongoDB, Redis (caching, locking), Stored Procedures, B-Tree Indexing</div>
    <div><strong>Security & Auth:</strong> JWT, OAuth2, Role-Based Access Control (RBAC), Idempotency, Session Management</div>
    <div><strong>Cloud & DevOps:</strong> Docker, AWS (EC2, S3), CI/CD (GitHub Actions), Linux, Postman, Git</div>
    <div><strong>Core Computer Science:</strong> Data Structures & Algorithms, System Design (HLD/LLD), Operating Systems, DBMS</div>
  </div>

  <div class="section-title">Professional Experience</div>

  <div class="job-header">
    <span>Software Developer (Enterprise Backend & Systems)</span>
    <span>July 2024 – Present</span>
  </div>
  <div class="job-sub">
    <span>NexGen</span>
    <span>Noida, India</span>
  </div>
  <ul>
    <li>Architected and maintain <strong>250+ RESTful APIs</strong> for core multi-tenant ERP platforms using Node.js, Express, and Flask over MySQL and MongoDB, powering daily operations for business teams.</li>
    <li>Engineered Identity & Access Management (IAM) with <strong>JWT, OAuth2, and RBAC</strong>, securing enterprise tenants with sub-second role authorization.</li>
    <li>Built an <strong>Automated Reconciliation Engine</strong> in Python and SQL for scheduled ledger balancing and batch syncs, cutting manual accounting overhead by <strong>70%</strong>.</li>
    <li>Optimized complex stored procedures, query indexes, and execution plans on MySQL and SQL Server, achieving a <strong>35% latency reduction</strong> for high-concurrency bulk transactions.</li>
    <li>Introduced <strong>Redis caching</strong> for frequently accessed master reference data, lowering database IOPS by over 50% and accelerating hot endpoints.</li>
    <li>Containerized monolithic services into decoupled <strong>Docker microservices</strong> with automated CI/CD pipelines, upholding a <strong>99.9% uptime SLA</strong>.</li>
  </ul>

  <div class="job-header">
    <span>Software Development Engineer Intern (Web Products)</span>
    <span>Feb 2024 – June 2024</span>
  </div>
  <div class="job-sub">
    <span>Oasis InfoByte</span>
    <span>Remote, India</span>
  </div>
  <ul>
    <li>Shipped 5+ production e-commerce modules using React.js and TypeScript, reducing page-load latency by <strong>25%</strong> through memoization and state restructuring.</li>
    <li>Integrated asynchronous REST APIs with client-side caching within rapid 2-week Agile sprint cycles.</li>
  </ul>

  <div class="section-title">Key Technical Projects</div>

  <div class="job-header">
    <span>Warehouse Automation System (IIoT Telemetry)</span>
    <span>Python, Flask, WebSockets, MySQL, Docker</span>
  </div>
  <ul>
    <li>Built a real-time telemetry pipeline from factory PLC hardware (Siemens S7/Snap7) to Flask services with <strong>5–10ms latency</strong> and <strong>99.2% accuracy</strong> under burst loads.</li>
    <li>Delivered a live WebSocket operator dashboard with automated fault alerting, reducing equipment troubleshooting downtime by 40%.</li>
  </ul>

  <div class="job-header">
    <span>Distributed API Gateway with Rate Limiting</span>
    <span>Node.js, Express, Redis, JWT, Docker</span>
  </div>
  <ul>
    <li>Designed an edge reverse-proxy gateway implementing token-bucket rate limiting via Redis, edge cryptographic JWT validation, and correlation ID tracing.</li>
  </ul>

  <div class="section-title">Achievements & Honors</div>
  <ul>
    <li><strong>GeeksforGeeks Top Competitive Programmer:</strong> Solved 800+ DSA problems; achieved peak global rank <strong>Top 28th out of 8,000+</strong> competitors.</li>
    <li><strong>KAVACH Cyber Security Hackathon (National):</strong> Secured <strong>8th position</strong> among 70+ finalist teams nationwide across India.</li>
    <li><strong>Production Engineering Velocity:</strong> Successfully shipped 6+ production-grade enterprise systems in year one at NexGen meeting 99.9% uptime SLAs.</li>
  </ul>

  <div class="section-title">Education</div>
  <div class="job-header">
    <span>Bachelor of Technology in Information Technology</span>
    <span>2020 – 2024</span>
  </div>
  <div class="job-sub">
    <span>Ajay Kumar Garg Engineering College (AKGEC)</span>
    <span>Ghaziabad, India (CGPA: 7.64 / 10)</span>
  </div>
</body>
</html>
"""

    @staticmethod
    def _build_latex_cv(candidate: Dict[str, Any], summary: str, company: str, role: str) -> str:
        name = candidate.get("name", "Shreyash Shukla")
        first_name = name.split()[0] if " " in name else name
        last_name = name.split()[1] if " " in name else ""
        return f"""\\documentclass[11pt,a4paper,sans]{{moderncv}}
\\moderncvstyle{{banking}}
\\moderncvcolor{{blue}}
\\usepackage[utf8]{{inputenc}}
\\usepackage[scale=0.82]{{geometry}}

\\name{{{first_name}}}{{{last_name}}}
\\address{{{candidate.get('location', 'India')}}}{{}}{{}}
\\phone[mobile]{{{candidate.get('phone', '+91 6306211105')}}}
\\email{{{candidate.get('email', 'shreyashshukla7398554573@gmail.com')}}}
\\extrainfo{{\\href{{{candidate.get('linkedin_url', 'https://linkedin.com/in/shuklashreyash')}}}{{LinkedIn}} | \\href{{{candidate.get('github_url', 'https://github.com/shreyash418')}}}{{GitHub}} | \\href{{https://auth.geeksforgeeks.org/user/shuklashreyash}}{{GFG Rank 28/8k+}}}}

\\begin{{document}}
\\makecvtitle

\\vspace{{-12pt}}
\\small{{{summary}}}

\\section{{Technical Skills}}
\\begin{{itemize}}
\\item \\textbf{{Languages}}: C++, Python, JavaScript (ES6+), TypeScript, SQL, HTML5, CSS3
\\item \\textbf{{Backend and APIs}}: Node.js, Express.js, Flask, RESTful APIs, Microservices, Redis, JWT, OAuth2, RBAC, WebSockets
\\item \\textbf{{Databases}}: MS SQL Server, MySQL, MongoDB, Redis Caching, Stored Procedures, B-Tree Index Tuning
\\item \\textbf{{DevOps and Tools}}: Docker, AWS (EC2, S3), CI/CD (GitHub Actions), Linux, Git, Postman
\\item \\textbf{{Core CS}}: Data Structures and Algorithms, System Design (HLD/LLD), Operating Systems, DBMS
\\end{{itemize}}

\\section{{Professional Experience}}
\\begin{{itemize}}
\\item{{\\cventry{{July 2024 -- Present}}{{Software Developer (Enterprise Backend)}}{{NexGen}}{{Noida, India}}{{}}{{\\vspace{{1pt}}
\\begin{{itemize}}
  \\item Architected and maintain 250+ RESTful APIs for enterprise platforms using Node.js, Express, and SQL/MongoDB.
  \\item Optimized query execution plans and B-Tree indexes, achieving a 35\\% latency reduction on bulk transactions.
  \\item Built an Automated Reconciliation Engine (Python, SQL), eliminating 70\\% of manual accounting hours.
  \\item Sustained a 99.9\\% uptime SLA across high-availability microservices with Docker and Redis caching.
\\end{{itemize}}}}}}
\\end{{itemize}}

\\section{{Key Technical Projects}}
\\begin{{itemize}}
\\item{{\\cventry{{2024}}{{Warehouse Automation System (IIoT Telemetry)}}{{Python, Flask, WebSockets, MySQL, Docker}}{{Real-Time Systems}}{{}}{{\\vspace{{1pt}}
\\begin{{itemize}}
  \\item Built real-time telemetry pipeline from factory PLC hardware to Flask services with 5--10ms latency and 99.2\\% accuracy.
  \\item Delivered live WebSocket dashboard reducing machinery troubleshooting downtime by 40\\%.
\\end{{itemize}}}}}}
\\end{{itemize}}

\\section{{Achievements and Honors}}
\\begin{{itemize}}
\\item \\textbf{{GeeksforGeeks}}: Solved 800+ DSA problems; Global Rank \\textbf{{Top 28th out of 8,000+}} users.
\\item \\textbf{{KAVACH Hackathon}}: Secured \\textbf{{8th position}} among 70+ finalist teams across India.
\\end{{itemize}}

\\end{{document}}
"""

    @staticmethod
    def _build_text_cv(candidate: Dict[str, Any], summary: str) -> str:
        return f"""SHREYASH SHUKLA
Backend / Systems Software Engineer
Noida, India (Open to Bengaluru & Remote) | +91 6306211105 | shreyashshukla7398554573@gmail.com
LinkedIn: linkedin.com/in/shuklashreyash | GitHub: github.com/shreyash418 | GFG: Rank 28/8,000+

SUMMARY:
{summary}

TECHNICAL SKILLS:
- Languages: C++, Python, JavaScript (ES6+), TypeScript, SQL
- Backend & APIs: Node.js, Express.js, Flask, RESTful APIs, Microservices, WebSockets, Rate Limiting
- Databases & Storage: MS SQL Server, MySQL, MongoDB, Redis Caching, Stored Procedures, B-Tree Indexing
- Cloud & DevOps: Docker, AWS (EC2, S3), CI/CD (GitHub Actions), Linux, Git, Postman
- Core CS: Data Structures & Algorithms (800+ solved, GFG Rank 28/8k+), System Design (HLD/LLD)

EXPERIENCE:
Software Developer | NexGen (July 2024 - Present)
- Architected and maintain 250+ RESTful APIs for core Enterprise ERP platforms.
- Achieved a 35% latency reduction on high-concurrency bulk transactions via SQL execution plan and index tuning.
- Built an Automated Reconciliation Engine in Python, cutting manual accounting effort by 70%.
- Maintained a 99.9% uptime SLA across Dockerized microservices with Redis caching.

SDE Intern | Oasis InfoByte (Feb 2024 - June 2024)
- Delivered 5+ production e-commerce modules with React and TypeScript, cutting page-load times by 25%.

PROJECTS:
- Warehouse Automation System (IIoT): 5-10ms response latency telemetry pipeline from PLCs to Flask services with 99.2% accuracy.
- Distributed API Gateway: Redis token-bucket rate limiting, JWT validation, and Dockerized CI/CD.

ACHIEVEMENTS:
- Solved 800+ DSA problems; Ranked 28th out of 8,000+ users on GeeksforGeeks.
- 8th position among 70+ teams in KAVACH National Cyber Security Hackathon.
"""

    @classmethod
    def calculate_salary_benchmark(
        cls,
        role: str,
        experience_years: float = 2.0,
        location: str = "Bengaluru",
        company_tier: str = "tier1"
    ) -> Dict[str, Any]:
        """Calculates precise salary and ESOP benchmark data with negotiation script."""
        is_remote_usd = "global" in location.lower() or "worldwide" in location.lower() or "usd" in location.lower()

        if is_remote_usd:
            base_min = "$70,000 USD (₹59L)"
            base_max = "$110,000 USD (₹92L)"
            bonus = "10% - 15% Annual Performance"
            esops = "$15,000 - $35,000 USD Stock Grants (4-yr vest)"
            total = "$85,000 - $130,000 USD / year"
        else:
            # India Market Benchmarks for 2+ YoE (SDE-1 / SDE-2)
            if company_tier == "tier1": # CRED, Razorpay, Zepto, Swiggy, InMobi
                base_min = "₹22L Fixed"
                base_max = "₹34L Fixed"
                bonus = "₹2L - ₹4L Variable"
                esops = "₹8L - ₹18L over 4 years"
                total = "₹26L - ₹40L CTC"
            elif company_tier == "growth_unicorn": # Meesho, Groww, Delhivery, CarDekho
                base_min = "₹18L Fixed"
                base_max = "₹28L Fixed"
                bonus = "₹1.5L - ₹3L Variable"
                esops = "₹5L - ₹12L over 4 years"
                total = "₹21L - ₹32L CTC"
            else: # Early Stage Funded Startups (Pre-Seed, Series A)
                base_min = "₹16L Fixed"
                base_max = "₹24L Fixed"
                bonus = "₹1L - ₹2L"
                esops = "0.15% - 0.50% Heavy Equity ($20k - $50k value)"
                total = "₹18L - ₹28L + High Upside Equity"

        insights = [
            f"For 2+ years experience in {location}, top-tier product startups are actively paying {base_min} to {base_max}.",
            "Your 250+ production APIs and Top 28 GFG ranking place you in the top 5% of candidate profiles in technical screens.",
            "Always negotiate on Fixed Base salary first before accepting higher variable bonus or unvested ESOP promises."
        ]

        script = (
            f"\"Based on my production track record architecting 250+ APIs, reducing transaction latency by 35%, and my "
            f"top 28 rank on GeeksforGeeks, I am targeting roles in the {base_min} - {base_max} fixed range. "
            f"I have a strong bias for high-impact teams and am excited by {company_tier.replace('_', ' ').title()} challenges, "
            f"so I am open to discussing a balanced package with equity.\""
        )

        return {
            "base_min": base_min,
            "base_max": base_max,
            "bonus_estimate": bonus,
            "esop_estimate": esops,
            "total_ctc_range": total,
            "insights": insights,
            "negotiation_script": script
        }

    @classmethod
    def ai_dsa_tutor(
        cls,
        title: str,
        pattern: str,
        language: str = "python",
        mode: str = "dry_run",
        user_input: str = "",
        preferred: str = "groq",
        gemini_key: Optional[str] = None,
        groq_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """Interactive AI DSA tutor for dry runs, edge cases, debugging, and follow-up twists."""
        lang_label = "C++17" if language == "cpp" else "Python 3"
        mode_instructions = {
            "dry_run": f"Walk through a crisp step-by-step dry run trace on a concrete example (or the user's input: '{user_input}') showing exact variable states at each iteration.",
            "hint": "Give 3 progressive hints without spoiling the full code immediately, ending with the core invariant.",
            "quiz": "Act as a senior interviewer at Razorpay/Amazon. Ask ONE tough follow-up constraint twist (e.g. streaming input, O(1) space, or concurrency) and briefly explain what you look for.",
            "debug": f"Inspect this user code/idea in {lang_label} and spot any off-by-one, edge-case, or complexity bugs:\n{user_input}"
        }
        task = mode_instructions.get(mode, mode_instructions["dry_run"])
        prompt = f"""You are a Senior FAANG/Startup DSA Coach helping a 2+ YoE Backend Engineer prepare in {lang_label}.
Problem: {title}
Pattern: {pattern}
Task: {task}
Keep it concise, crisp, visual (use clear step lines/arrows), and highlight time/space complexity + edge cases."""

        text, used = cls.execute_llm_prompt(prompt, preferred=preferred, gemini_key=gemini_key, groq_key=groq_key)
        if text:
            return {"response": text, "provider": used}

        # Deterministic offline tutor fallback
        return {
            "provider": "offline",
            "response": (
                f"[{pattern} Coaching for {title} ({lang_label})]\n\n"
                f"1. Core Recognition: Look for the '{pattern}' invariant before writing loops.\n"
                f"2. Edge Cases to Verify First: Empty input, single element, duplicate keys, negative/zero values, integer overflow (use long long in C++ if summing).\n"
                f"3. Dry Run Tip: Trace pointer movement / state transitions step-by-step on a 4-element test array.\n"
                f"4. Connect your Groq key in Settings for custom input tracing & live bug detection!"
            )
        }

    @classmethod
    def ai_system_design_review(
        cls,
        case_title: str,
        user_design: str,
        preferred: str = "groq",
        gemini_key: Optional[str] = None,
        groq_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """Evaluates user's system design trade-offs like a Staff Backend Architect."""
        prompt = f"""You are a Principal/Staff Software Architect reviewing a candidate's System Design answer.
Case Study: {case_title}
Candidate's Proposal:
{user_design}

Provide a crisp structured review covering:
1. Score (/10) & What You Nailed
2. Bottlenecks / Failure Modes Missed (hot keys, split-brain, idempotency, backpressure, DB locks)
3. Exact Production Improvement (1 concrete upgrade using Redis/Kafka/DB indexing/partitioning)
Keep under 220 words."""

        text, used = cls.execute_llm_prompt(prompt, preferred=preferred, gemini_key=gemini_key, groq_key=groq_key)
        if text:
            return {"review": text, "provider": used}

        return {
            "provider": "offline",
            "review": (
                f"Architecture Review Checklist for {case_title}:\n"
                "• Bottleneck Check: Verify single points of failure on your write database—add connection pooling & read replicas.\n"
                "• Concurrency Check: Protect critical state transitions with Redis distributed locks (SETNX + TTL) or DB optimistic versioning.\n"
                "• Reliability Check: Decouple burst writes using an async queue (BullMQ/Kafka) with idempotency keys & Dead Letter Queues.\n"
                "• Configure your Groq/Gemini key in Settings for personalized AI critique on your exact answer."
            )
        }

    @classmethod
    def ai_screening_answer(
        cls,
        company: str,
        role: str,
        question: str,
        jd_text: str,
        candidate_data: Dict[str, Any],
        preferred: str = "groq",
        gemini_key: Optional[str] = None,
        groq_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generates sharp, metric-backed answers for LinkedIn Easy Apply / Google Form screening questions."""
        prompt = f"""Write a concise, high-impact application screening answer (2-4 sentences, ready to paste into LinkedIn Easy Apply or an ATS form).
Candidate: {candidate_data.get('name', 'Shreyash Shukla')} — Backend/Full-Stack Engineer (2+ YoE, Node.js, Express, Python, SQL, Redis, Docker, AWS).
Real Verified Metrics: Built 250+ RESTful APIs at NexGen, reduced SQL transaction latency by 35% via composite B-Tree indexing, cut manual reconciliation 70% via Python automation, sustained 99.9% uptime SLA, GFG Institute Rank #28 (800+ DSA solved).
Target: {role} at {company}
JD Context: {(jd_text or '')[:800]}
Screening Question: {question}

Rules: Be natural, direct, zero buzzword fluff, zero em-dashes, anchor to real metrics."""

        text, used = cls.execute_llm_prompt(prompt, preferred=preferred, gemini_key=gemini_key, groq_key=groq_key)
        if text:
            return {"answer": text, "provider": used}

        return {
            "provider": "offline",
            "answer": (
                f"With 2+ years of production backend experience architecting 250+ RESTful APIs in Node.js and Python, "
                f"I have delivered measurable scale improvements including a 35% reduction in database query latency through SQL index tuning "
                f"and 99.9% microservice uptime using Redis caching and Docker. I am excited to bring this ownership mindset to {company}'s {role} team."
            )
        }

    @classmethod
    def ai_mock_grill(
        cls,
        company: str,
        role: str,
        question: str,
        user_answer: str,
        focus_area: str = "backend",
        preferred: str = "groq",
        gemini_key: Optional[str] = None,
        groq_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """Interactive AI interviewer grill mode: scores candidate answer and asks next follow-up."""
        prompt = f"""You are a tough yet constructive Senior Engineering Interviewer at {company} interviewing for {role} (Focus: {focus_area}).
Previous Question Asked: {question}
Candidate's Answer: {user_answer}

Respond strictly in valid JSON with keys:
{{
  "score": <1 to 10 integer>,
  "feedback": "<2-3 sentences highlighting technical accuracy, depth, and missing edge cases>",
  "ideal_bullet": "<1 sentence showing how a top 1% SDE-2 frames this>",
  "next_question": "<1 sharp follow-up question digging deeper or pivoting to scale/edge cases>"
}}
Return ONLY raw JSON."""

        text, used = cls.execute_llm_prompt(prompt, preferred=preferred, gemini_key=gemini_key, groq_key=groq_key)
        if text:
            try:
                cleaned = re.sub(r"^```json\s*|^```\s*|\s*```$", "", text.strip(), flags=re.MULTILINE)
                parsed = json.loads(cleaned)
                parsed["provider"] = used
                return parsed
            except Exception:
                return {
                    "score": 8,
                    "feedback": text[:500],
                    "ideal_bullet": "Tie architecture choices back to P99 latency, failure recovery, and measurable production SLAs.",
                    "next_question": f"How would your design handle a 10x burst in concurrent writes at {company} without dropping requests?",
                    "provider": used
                }

        return {
            "score": 8,
            "feedback": "Solid core reasoning. Strengthen your answer by explicitly stating time/space trade-offs, failure fallback behavior, and concrete numbers (latency, throughput, or DB lock scope).",
            "ideal_bullet": "Always quantify the bottleneck (e.g., B-Tree composite index dropped P99 from 850ms to <45ms) before explaining the fix.",
            "next_question": f"What happens in your {focus_area} solution if Redis or the primary cache node restarts under peak load?",
            "provider": "offline"
        }

    @classmethod
    def universal_ai_search(
        cls,
        query: str,
        mode: str = "general",
        preferred: str = "groq",
        gemini_key: Optional[str] = None,
        groq_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """Custom AI research agent answering any tech, company intel, system design, or interview question."""
        mode_instructions = {
            "company": "You are a Principal Tech Recruiter and Staff Engineer with deep insider knowledge of Indian and global tech companies (startups, unicorns, MNCs). Provide real interview rounds, tech stack specifics, engineering culture, and compensation benchmarks.",
            "concept": "You are a Staff Distributed Systems Engineer and CS Professor. Explain technical concepts with crystal-clear intuition, diagrams in ASCII or Mermaid where useful, code snippets in Python/C++, and real-world production trade-offs.",
            "interview": "You are an Elite Tech Interview Coach for top-tier product companies (Swiggy, Razorpay, Google, Zepto, CRED). Provide high-scoring STAR responses, killer reverse questions, and architectural insights.",
            "salary": "You are a Silicon Valley & Indian Tech Compensation Specialist. Provide realistic base, ESOPs, bonus benchmarks, and word-for-word negotiation scripts.",
            "general": "You are an advanced Engineering AI Assistant (CareerOS Intelligence, like Gemini & Grok). Provide structured, technically accurate, and concise answers with code where relevant."
        }
        inst = mode_instructions.get(mode, mode_instructions["general"])
        prompt = f"""{inst}

User Query:
{query}

Formatting Guidelines:
- Structure with clear Markdown headers (###), bullet points, and clean syntax-highlighted code blocks where helpful.
- Be direct, insightful, and practical—no unnecessary preamble.
- Cite specific technologies, metrics, and production patterns where appropriate.
"""
        text, used = cls.execute_llm_prompt(prompt, preferred=preferred, gemini_key=gemini_key, groq_key=groq_key)
        if not text:
            text = f"### CareerOS AI Analysis for: {query}\n\n1. **Core Insight**: In modern high-scale engineering, focus on database indexing, distributed caching (Redis), and event-driven architecture (Kafka/SQS).\n2. **Interview Advice**: Quantify impact using the Google XYZ formula (Achieved X, measured by Y, by doing Z).\n3. **Production Metric**: Always architect for sub-50ms P99 latency and fault tolerance with graceful degradation."
            used = "CareerOS Engine"
        return {
            "answer": text,
            "result": text,
            "provider": used,
            "mode": mode,
            "query": query
        }
