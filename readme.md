# 🚀 LLM Code Deployment – FastAPI + GitHub Automation

This project provides a **FastAPI-based automation API** that takes JSON input to **generate, update, and deploy static web applications to GitHub Pages** using **GitHub Copilot CLI**.

It automates:
1. Generating code using GitHub Copilot CLI.
2. Saving round-based assets and updates.
3. Creating/pushing to GitHub repositories.
4. Enabling GitHub Pages hosting automatically.
5. Optionally notifying an evaluation endpoint.

---

## ⚙️ Features

- **FastAPI server** (`api_server.py`) that accepts JSON tasks.
- **Code builder** (`check.py`) that runs Copilot CLI, commits, pushes, and publishes to GitHub Pages.
- **Testing script** (`test_api.py`) for verifying endpoints.
- **Round-based workflow** — round 1 creates a new repo, later rounds update it.
- **MIT License generation** and professional README automation.

---

## 📦 Project Structure

```
LLM-Code-Deployment/
│
├── api_server.py     # FastAPI server (handles incoming JSON + background processing)
├── check.py          # Core logic for code generation, GitHub commits, and deployment
├── test_api.py       # Local/remote API tester
├── .env              # Environment variables (see below)
└── requirements.txt  # Dependencies
```

---

## 🔑 Environment Variables

Create a `.env` file in the root directory with the following variables:

```bash
API_SECRET=your_api_secret_here
GITHUB_TOKEN=your_github_personal_access_token
GITHUB_USERNAME=your_github_username
```

> 🧠 **Tip:** You have to generate Personal Access Token(classic) and have to give repo and workflow permissions.

---
## 🧩 Local Setup

1. **Clone Repository**

```bash
git clone https://github.com/23f3003494/LLM-Code-Deployment.git
cd LLM-Code-Deployment
```

2. **Install Dependencies**

```bash
pip install -r requirements.txt
```

3. **Run FastAPI Server**

```bash
uvicorn api_server:app --port 5000
```

**Server runs at → http://127.0.0.1:5000**

4. **Test API**

You can test your API locally or via Cloudflare tunnel using:

```bash
python test_api.py
```

## 🧠 API Overview

### **POST** `/run-task`

**Request Body (JSON)**

```json
{
  "email": "student@example.com",
  "secret": "your_api_secret",
  "task": "captcha-solver-001",
  "round": 1,
  "nonce": "xyz-123",
  "brief": "Generate a static website that solves captchas.",
  "checks": [
    "README.md is professional",
    "Captcha image loads correctly"
  ],
  "evaluation_url": "https://example.com/notify",
  "attachments": [
    { "name": "sample.png", "url": "data:image/png;base64,..." }
  ]
}
```

**Response with 200 to caller**
```json
{
  "email": "student@example.com",
  "task": "captcha-solver-001",
  "round": 1,
  "nonce": "xyz-123",
  "status": "Processing started"
}
```
**POST request to evaluation_url**
```json
{
  "email": "student@example.com",
  "task": "captcha-solver-001",
  "round": 1,
  "nonce": "xyz-123",
  "repo_url": created_repo_url,
  "commit_sha": commit_sha,
  "pages_url": static_site_url
}
```
---

## 🧱 How It Works (Pipeline)

1. `POST /run-task` receives a JSON payload.
2. `api_server.py` validates the secret and runs `check.py` in the background.
3. `check.py`:
   - Saves provided attachments.
   - Invokes GitHub Copilot CLI (`npx @github/copilot`) with a task prompt.
   - Initializes a Git repository and commits generated files.
   - Creates a remote GitHub repo and pushes code.
   - Enables GitHub Pages automatically.
4. Final repo and site URLs are sent to the `evaluation_url` if provided.

---

## 🧰 Tech Stack

- **FastAPI** – REST API server
- **GitHub Copilot CLI** – Code generation
- **GitHub REST API** – Repo creation and Pages enablement
- **Python Dataclasses** – Data modeling
- **dotenv** – Secure environment variable loading
- **requests** – Web communication
- **subprocess** – Git and CLI automation

---

## 🧪 Example Workflow

```bash
curl -X POST "http://127.0.0.1:5000/run-task"      -H "Content-Type: application/json"      -d @example_task.json
```

---

## 🧑‍💻 Author

**Madhavanand Murty**  
🔗 [GitHub Profile](https://github.com/23f3003494)  
💡 Created for automated AI-driven web deployment workflows.

---

## 🪪 License

This project is licensed under the [MIT License](LICENSE).

uvicorn api_server:app --port 5000

cloudflared tunnel --url http://127.0.0.1:5000


