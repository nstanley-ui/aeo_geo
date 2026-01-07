from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import json
import os

app = FastAPI()

# Allow CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/analyze")
async def analyze(domain: str = Query("ironhorse.io")):
    # 1. Run AEO check
    aeo_result = subprocess.run(
        ["python", "execution/check_aeo.py", domain],
        capture_output=True, text=True
    )
    aeo_data = json.loads(aeo_result.stdout) if aeo_result.returncode == 0 else {"error": "AEO check failed"}
    
    # 2. Run Social audit
    social_result = subprocess.run(
        ["python", "execution/check_socials.py", domain],
        capture_output=True, text=True
    )
    social_data = json.loads(social_result.stdout) if social_result.returncode == 0 else {"error": "Social audit failed"}
    
    return {
        "domain": domain,
        "aeo": aeo_data,
        "social": social_data,
        "overall_score": (aeo_data.get("aeo_score", 0) + social_data.get("overall_social_score", 0)) // 2,
        "optimized_files": aeo_data.get("optimized_files", {}),
        "advanced_checks": aeo_data.get("advanced_checks", {})
    }

@app.get("/competitors")
async def get_competitors(domain: str = Query("ironhorse.io")):
    result = subprocess.run(
        ["python", "execution/check_competitors.py", domain],
        capture_output=True, text=True
    )
    return json.loads(result.stdout) if result.returncode == 0 else {"error": "Competitor check failed"}

@app.get("/generate-files")
async def generate_files(domain: str = Query("ironhorse.io")):
    """Generate optimized AEO files by crawling the domain."""
    result = subprocess.run(
        ["python", "execution/crawl_site.py", domain],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        return json.loads(result.stdout)
    else:
        return {"error": "File generation failed", "details": result.stderr}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

