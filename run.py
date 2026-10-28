import sys
import os

if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import uvicorn

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    print("=" * 60)
    print(f"[*] Starting CareerOS on http://{host}:{port}")
    print(f"[*] API Docs:  http://{host}:{port}/docs")
    print(f"[*] Pre-seeded User: Shreyash Shukla (shreyashshukla7398554573@gmail.com)")
    print("=" * 60)
    
    uvicorn.run("app.main:app", host=host, port=port, reload=False)
