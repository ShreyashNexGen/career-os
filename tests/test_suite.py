import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Ensure sqlite for testing
os.environ["DATABASE_URL"] = "sqlite:///./test_careeros.db"

from fastapi.testclient import TestClient
from app.main import app
from app.services.job_service import JobService
from app.services.ai_service import AIService

class CareerOSTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        # Login or get token for user
        email = "test_shreyash@example.com"
        password = "password123"
        reg = cls.client.post("/api/auth/register", json={
            "email": email,
            "full_name": "Shreyash Shukla",
            "password": password
        })
        res = cls.client.post("/api/auth/login", json={"email": email, "password": password})
        cls.token = res.json().get("access_token")
        cls.headers = {"Authorization": f"Bearer {cls.token}"}

    def test_01_public_ats_expansion(self):
        """Verify Greenhouse + Ashby + Lever ATS scrapers return direct application URLs"""
        jobs = JobService.fetch_public_ats_jobs()
        self.assertGreater(len(jobs), 0, "Should fetch live ATS jobs")
        first_job = jobs[0]
        self.assertTrue(first_job.get("is_direct"), "ATS jobs must have is_direct=True")
        self.assertIn("Direct", first_job.get("source_badge", ""))
        self.assertTrue(first_job.get("url", "").startswith("http"), "Must have valid HTTP apply url")
        print(f"[PASS] test_01_public_ats_expansion: Fetched {len(jobs)} direct ATS jobs. Sample: {first_job['company']} - {first_job['title']}")

    def test_02_radar_source_filter(self):
        """Verify /api/radar/jobs supports source_filter=direct_ats and source_filter=all"""
        # test all
        res_all = self.client.get("/api/radar/jobs?source_filter=all", headers=self.headers)
        self.assertEqual(res_all.status_code, 200)
        jobs_all = res_all.json()
        self.assertGreater(len(jobs_all), 0)

        # test direct_ats
        res_direct = self.client.get("/api/radar/jobs?source_filter=direct_ats", headers=self.headers)
        self.assertEqual(res_direct.status_code, 200)
        jobs_direct = res_direct.json()
        self.assertGreater(len(jobs_direct), 0)
        for j in jobs_direct:
            self.assertTrue(j.get("is_direct"), f"Job {j['title']} must be direct ATS")
        print(f"[PASS] test_02_radar_source_filter: all={len(jobs_all)} jobs, direct_ats={len(jobs_direct)} jobs")

    def test_03_dsa_endpoints_and_gfg(self):
        """Verify /api/dsa returns 200 with gfg_url, leetcode_url, and progressive hints"""
        res = self.client.get("/api/dsa", headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        problems = data.get("problems", [])
        self.assertGreater(len(problems), 0)
        sample = problems[0]
        self.assertIn("gfg_url", sample)
        self.assertIn("leetcode_url", sample)
        self.assertTrue(sample["gfg_url"].startswith("http"))
        self.assertTrue(sample["leetcode_url"].startswith("http"))
        self.assertIn("python_code", sample)
        self.assertIn("cpp_code", sample)
        print(f"[PASS] test_03_dsa_endpoints_and_gfg: Checked {len(problems)} DSA problems with GFG & LC links")

    def test_04_sysdesign_notes_and_progress(self):
        """Verify /api/sysdesign returns progress and notes maps, and /api/learning/progress persists notes"""
        # Update progress and notes
        update_res = self.client.post("/api/learning/progress", json={
            "category": "sysdesign",
            "item_id": "url-shortener",
            "status": "solved",
            "notes": "Key math: 100M URLs/mo = 40 writes/sec. 7-char Base62 gives 3.5T unique keys."
        }, headers=self.headers)
        self.assertEqual(update_res.status_code, 200)

        # Fetch sysdesign hub
        res = self.client.get("/api/sysdesign", headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("notes", data)
        self.assertIn("progress", data)
        self.assertEqual(data["progress"].get("url-shortener"), "solved")
        self.assertIn("Key math", data["notes"].get("url-shortener", ""))
        print("[PASS] test_04_sysdesign_notes_and_progress: Notes and status saved and retrieved successfully")

    def test_05_universal_ai_search(self):
        """Verify /api/ai/universal-search handles query and returns structured response"""
        res = self.client.post("/api/ai/universal-search", json={
            "query": "What are the core rounds for SDE-2 at Postman and what backend topics are grilled?",
            "mode": "company"
        }, headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("result", data)
        self.assertIn("provider", data)
        self.assertEqual(data.get("mode"), "company")
        self.assertGreater(len(data["result"]), 50)
        print(f"[PASS] test_05_universal_ai_search: Engine={data['provider'].upper()}, Result length={len(data['result'])} chars")

    def test_06_custom_document_vault(self):
        """Verify /api/documents/custom saves an AI research document to Document Vault"""
        res = self.client.post("/api/documents/custom", json={
            "title": "Zepto SDE-2 System Design Intel",
            "category": "ai_research",
            "content": "Zepto 10-minute grocery delivery architecture: QuadTree geo-indexing, Redis pub/sub dark store rider assignment."
        }, headers=self.headers)
        self.assertEqual(res.status_code, 200)
        doc = res.json()
        self.assertEqual(doc["company"], "CareerOS Intel")
        self.assertEqual(doc["role"], "Zepto SDE-2 System Design Intel")

        # Verify it shows in GET /api/documents
        list_res = self.client.get("/api/documents", headers=self.headers)
        self.assertEqual(list_res.status_code, 200)
        docs = list_res.json()
        saved_doc = next((d for d in docs if d["id"] == doc["id"]), None)
        self.assertIsNotNone(saved_doc)
        print(f"[PASS] test_06_custom_document_vault: Document saved & listed with ID={doc['id']}")

    @classmethod
    def tearDownClass(cls):
        if os.path.exists("./test_careeros.db"):
            try:
                os.remove("./test_careeros.db")
            except Exception:
                pass

if __name__ == "__main__":
    unittest.main()
