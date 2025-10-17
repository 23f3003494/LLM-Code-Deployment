import os
import json
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import requests
from check import run_check  # import your function

# Load environment variables
load_dotenv()

API_SECRET = os.getenv("API_SECRET")
if not API_SECRET:
    raise RuntimeError("API_SECRET not found in .env")

app = FastAPI(title="GitHub Automation API", version="1.0")


@app.post("/run-task")
async def run_task(request: Request):
    """Receive JSON, verify secret, pass to check.py, return repo info."""
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    # Validate secret
    if data.get("secret") != API_SECRET:
        raise HTTPException(status_code=403, detail="Unauthorized: invalid secret")

    # Validate required fields
    for field in ["email", "task", "round", "nonce"]:
        if field not in data:
            raise HTTPException(status_code=400, detail=f"Missing field: {field}")
    # Extract evaluation URL
    evaluation_url = data.get("evaluation_url")
    try:
        # Call your check.py function directly
        repo_url, commit_sha, site_url = run_check(data)

        # Build the response JSON
        response_payload = {
            "email": data["email"],
            "task": data["task"],
            "round": data["round"],
            "nonce": data["nonce"],
            "repo_url": repo_url,
            "commit_sha": commit_sha,
            "pages_url": site_url
        }

        # Send response to evaluation_url if provided
        if evaluation_url:
            try:
                eval_resp = requests.post(
                    evaluation_url,
                    json=response_payload,
                    headers={"Content-Type": "application/json"},
                    
                )
                print(f"✅ Sent results to evaluation_url: {evaluation_url} - Status {eval_resp.status_code}")
            except Exception as e:
                print(f"❌ Failed to notify evaluation_url: {e}")

        # Return the same JSON to the API caller
        return JSONResponse(content=response_payload, status_code=200)

    except Exception as e:
        # Even if run_check fails, you can return 200 with error details if desired
        print("❌ Error running task:", e)
        return JSONResponse(
            content={"error": str(e), "message": "Failed to run task"},
            status_code=200
        )


@app.get("/")
def home():
    return {"message": "GitHub Automation API is running!"}
