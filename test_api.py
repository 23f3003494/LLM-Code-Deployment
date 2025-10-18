import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://127.0.0.1:5000"
API_SECRET = os.getenv("API_SECRET")

# -------------------------
# Test Payload
# -------------------------

# Enable this one for round 2
# test_payload ={
#   "email": "student@example.com",
#   "secret": API_SECRET,
#   "task": "captcha-solver-001",
#   "round": 2,
#   "nonce": "ab12-xyz",
#   "brief": "it should handle svg also passed by ?url=www.keshav.com/captcha.svg. Default to attached sample.",
#   "checks": [
    
#     "README.md is updated",
#     "Page displays both default images png and svg as passed in attachments",
#     "Page displays solved captchas text within 15 seconds"
#   ],
#   "evaluation_url": "https://example.com/notify",
#   "attachments": [{ "name": "sample.svg", "url": "data:image/svg;base64,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" }]
# }

#Enable it for round 1
test_payload = {
  "email": "student@example.com",
  "secret": API_SECRET,
  "task": "captcha-solver-001",
  "round": 1,
  "nonce": "ab12-xyz",
  "brief": "Create a captcha solver that handles ?url=www.keshav.com/captcha.svg. Default to attached sample.",
  "checks": [
    "Repo has MIT license"
    "README.md is professional",
    "Page displays captcha URL passed at ?url=...",
    "Page displays solved captcha text within 15 seconds",
  ],
  "evaluation_url": "https://example.com/notify",
  "attachments": [{ "name": "sample.png", "url": "data:image/png;base64,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" }]
}

def print_response(label, response):
    print("=" * 60)
    print(label)
    print(f"→ Status Code: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2))
    except Exception:
        print(response.text)
    print("=" * 60 + "\n")

def test_root():
    """Test root endpoint (GET /)"""
    resp = requests.get(f"{BASE_URL}/")
    print_response("Root Endpoint", resp)

def test_run_task_valid():
    """Test main run-task endpoint (POST /run-task)"""
    resp = requests.post(
        f"{BASE_URL}/run-task",
        json=test_payload,
        headers={"Content-Type": "application/json"}
    )
    print_response("Run Task (Valid Secret)", resp)


def test_run_task_invalid_secret():
    """Test /run-task with invalid secret"""
    invalid = test_payload.copy()
    invalid["secret"] = "wrong-secret"

    resp = requests.post(
        f"{BASE_URL}/run-task",
        json=invalid,
        headers={"Content-Type": "application/json"}
    )
    print_response("Run Task (Invalid Secret)", resp)

if __name__ == "__main__":
    print("\n🚀 Starting API Tests...\n")

    try:
        test_root()
       
        test_run_task_valid()
        test_run_task_invalid_secret()
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Could not connect to FastAPI server. Make sure it's running at", BASE_URL)
    except Exception as e:
        print("❌ ERROR:", str(e))


