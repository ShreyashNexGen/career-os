import os
import json
import re
import requests
from typing import Dict, Any, List

class AIService:

    @staticmethod
    def call_gemini(prompt: str, api_key: str) -> str:
        """Call Google Gemini 1.5 Flash API directly via standard REST."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 4096
            }
        }
        headers = {"Content-Type": "application/json"}
        resp = requests.post(url, headers=headers, json=payload, timeout=40)
        if resp.status_code != 200:
            raise Exception(f"Gemini API error ({resp.status_code}): {resp.text}")
        data = resp.json()
        candidates = data.get("candidates", [])
        if candidates and "content" in candidates[0]:
            parts = candidates[0]["content"].get("parts", [])
            if parts:
                return parts[0].get("text", "")
        return ""

    @staticmethod
    def call_groq(prompt: str, api_key: str) -> str:
        """Call Groq Cloud API directly via OpenAI-compatible endpoint."""
        url = "https://api.groq.com/openai/v1/chat/completions"
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": "You are an elite executive career advisor and technical recruiter."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 4096
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        if resp.status_code != 200:
            raise Exception(f"Groq API error ({resp.status_code}): {resp.text}")
        data = resp.json()
        choices = data.get("choices", [])
        if choices:
            return choices[0]["message"]["content"]
        return ""

    @classmethod
    def generate_tailored_package(
        cls,
        candidate_data: Dict[str, Any],
        job_description: str,
        company_name: str,
        role_title: str,
        api_key: str = None,
        provider: str = "gemini"
    ) -> Dict[str, Any]:
        """
        Orchestrates AI analysis and document generation.
        Falls back to rule-based generation if no API key or on provider failure.
        """
        # Attempt LLM generation if key is provided
        if api_key and provider in ["gemini", "groq"]:
            try:
                return cls._llm_tailor(candidate_data, job_description, company_name, role_title, api_key, provider)
            except Exception as e:
                print(f"[AIService Warning] LLM call failed ({str(e)}). Falling back to rule-based engine.")

        # Fallback to smart heuristic / template generator
        return cls._rule_based_tailor(candidate_data, job_description, company_name, role_title)

    @classmethod
    def _llm_tailor(cls, candidate: Dict[str, Any], jd: str, company: str, role: str, api_key: str, provider: str) -> Dict[str, Any]:
        prompt = f"""
You are an expert technical recruiter and resume strategist.
Candidate Profile:
{json.dumps(candidate, indent=2)}

Job Description for {role} at {company}:
{jd}

TASK:
Analyze the match and generate tailored application assets.
Return a STRICT valid JSON object with the following exact keys:
{{
  "fit_score": <integer from 0 to 100>,
  "fit_summary": "<2-3 sentences explaining strengths and fit>",
  "matching_skills": ["<skill 1>", "<skill 2>", ...],
  "missing_skills": ["<skill or gap>", ...],
  "tailored_profile_summary": "<3-4 sentence punchy profile summary highlighting matching metrics>",
  "tailored_cover_letter": "<Full professional 1-page cover letter, forward-looking, addressing company and role, no generic buzzwords, no em-dashes>",
  "outreach_linkedin_dm": "<Concise 3-paragraph outreach message to founder/recruiter under 250 words>",
  "outreach_cold_email": "<Full cold email with Subject and Body>"
}}
Return ONLY raw JSON, without markdown formatting or code fences.
"""
        raw_output = cls.call_gemini(prompt, api_key) if provider == "gemini" else cls.call_groq(prompt, api_key)
        # Clean json
        raw_output = re.sub(r"^```json\s*", "", raw_output.strip())
        raw_output = re.sub(r"^```\s*", "", raw_output)
        raw_output = re.sub(r"\s*```$", "", raw_output)

        data = json.loads(raw_output)

        # Build clean LaTeX and text
        latex_cv = cls._build_latex_cv(candidate, data.get("tailored_profile_summary", ""), company, role)
        cv_text = cls._build_text_cv(candidate, data.get("tailored_profile_summary", ""))

        return {
            "company_name": company,
            "role_title": role,
            "fit_score": int(data.get("fit_score", 85)),
            "fit_summary": data.get("fit_summary", "Strong technical match based on production backend experience."),
            "matching_skills": data.get("matching_skills", ["Node.js", "Express", "SQL", "Redis"]),
            "missing_skills": data.get("missing_skills", []),
            "tailored_cv_text": cv_text,
            "tailored_cv_latex": latex_cv,
            "tailored_cover_letter": data.get("tailored_cover_letter", ""),
            "outreach_linkedin_dm": data.get("outreach_linkedin_dm", ""),
            "outreach_cold_email": data.get("outreach_cold_email", "")
        }

    @classmethod
    def _rule_based_tailor(cls, candidate: Dict[str, Any], jd: str, company: str, role: str) -> Dict[str, Any]:
        """High-precision heuristic generator using candidate's verified metrics."""
        jd_lower = jd.lower()
        skills = candidate.get("skills", ["Node.js", "Express", "Python", "SQL", "Redis", "Docker", "REST APIs"])

        matched = [s for s in skills if s.lower() in jd_lower]
        if not matched:
            matched = ["Node.js", "Express", "SQL", "Redis", "Microservices"]

        fit_score = min(96, 75 + len(matched) * 3)

        summary = (
            f"Backend-focused Software Engineer with 2+ years of production experience architecting 250+ RESTful APIs "
            f"and scalable services in Node.js, Express, and Python. Proven track record in database performance optimization "
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

        linkedin_dm = f"""Hi Hiring Team / Founder at {company},

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

        latex_cv = cls._build_latex_cv(candidate, summary, company, role)
        cv_text = cls._build_text_cv(candidate, summary)

        return {
            "company_name": company,
            "role_title": role,
            "fit_score": fit_score,
            "fit_summary": f"Strong alignment on backend architecture, API scalability, and {', '.join(matched[:3])}.",
            "matching_skills": matched,
            "missing_skills": ["Domain-specific proprietary tools"],
            "tailored_cv_text": cv_text,
            "tailored_cv_latex": latex_cv,
            "tailored_cover_letter": letter,
            "outreach_linkedin_dm": linkedin_dm,
            "outreach_cold_email": cold_email
        }

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
\\extrainfo{{\\href{{{candidate.get('linkedin_url', 'https://linkedin.com/in/shuklashreyash')}}}{{LinkedIn}} | \\href{{{candidate.get('github_url', 'https://github.com/shreyash418')}}}{{GitHub}}}}

\\begin{{document}}
\\makecvtitle

\\vspace{{-12pt}}
\\small{{{summary}}}

\\section{{Technical Skills}}
\\begin{{itemize}}
\\item \\textbf{{Languages}}: C++, Python, JavaScript (ES6+), TypeScript, SQL, HTML5, CSS3
\\item \\textbf{{Backend}}: Node.js, Express.js, Flask, RESTful APIs, Microservices, Redis, JWT, OAuth2, RBAC
\\item \\textbf{{Databases}}: MS SQL Server, MySQL, MongoDB, Redis Caching, Stored Procedures, Index Tuning
\\item \\textbf{{DevOps & Tools}}: Docker, AWS (EC2, S3), CI/CD (GitHub Actions), Linux, Git, Postman
\\end{{itemize}}

\\section{{Professional Experience}}
\\begin{{itemize}}
\\item{{\\cventry{{July 2024 -- Present}}{{Software Developer}}{{NexGen}}{{Noida, India}}{{}}{{\\vspace{{1pt}}
\\begin{{itemize}}
  \\item Architected and maintain 250+ RESTful APIs for enterprise platforms using Node.js and SQL/MongoDB.
  \\item Optimized query execution plans and B-Tree indexes, achieving a 35\\% latency reduction on bulk transactions.
  \\item Built an Automated Reconciliation Engine (Python, SQL), eliminating 70\\% of manual accounting hours.
  \\item Sustained a 99.9\\% uptime SLA across high-availability microservices with Docker and Redis caching.
\\end{{itemize}}}}}}
\\end{{itemize}}

\\section{{Achievements}}
\\begin{{itemize}}
\\item \\textbf{{GeeksforGeeks}}: Solved 800+ DSA problems; Global Rank \\textbf{{28th out of 8,000+}} users.
\\item \\textbf{{KAVACH Hackathon}}: Secured \\textbf{{8th position}} among 70+ finalist teams across India.
\\end{{itemize}}

\\end{{document}}
"""

    @staticmethod
    def _build_text_cv(candidate: Dict[str, Any], summary: str) -> str:
        return f"""SHREYASH SHUKLA
Backend / Full Stack Software Engineer
Noida, India | +91 6306211105 | shreyashshukla7398554573@gmail.com | linkedin.com/in/shuklashreyash | github.com/shreyash418

SUMMARY:
{summary}

TECHNICAL SKILLS:
- Languages: C++, Python, JavaScript, TypeScript, SQL
- Backend & Architecture: Node.js, Express.js, Flask, REST APIs, Microservices, JWT, OAuth2, RBAC, Redis
- Databases & Storage: MS SQL Server, MySQL, MongoDB, Redis, B-Tree Indexing, Query Optimization
- Cloud & DevOps: Docker, AWS (EC2, S3), CI/CD (GitHub Actions), Linux, Git
- Core CS: Data Structures & Algorithms (800+ solved, GFG Rank 28/8k+), System Design (HLD/LLD)

EXPERIENCE:
Software Developer | NexGen (July 2024 - Present)
- Architected and maintain 250+ RESTful APIs for core Enterprise ERP platforms.
- Achieved a 35% latency reduction on high-concurrency bulk transactions via SQL index and query tuning.
- Built an Automated Reconciliation Engine in Python, cutting manual accounting effort by 70%.
- Maintained a 99.9% uptime SLA across Dockerized microservices with Redis caching.

SDE Intern | Oasis InfoByte (Feb 2024 - June 2024)
- Delivered 5+ production e-commerce modules with React and TypeScript, cutting load times by 25%.

PROJECTS:
- Warehouse Automation System (IIoT): 5-10ms latency telemetry pipeline from PLCs to Flask services with 99.2% accuracy.
- Distributed API Gateway: Redis token-bucket rate limiting, JWT validation, and Dockerized CI/CD.

ACHIEVEMENTS:
- Solved 800+ DSA problems; Ranked 28th out of 8,000+ users on GeeksforGeeks.
- 8th position among 70+ teams in KAVACH National Cyber Security Hackathon.
"""
