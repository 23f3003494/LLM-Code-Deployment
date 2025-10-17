import json
import os
from typing import List
import subprocess
from dataclasses import dataclass

# ---------- Define Models ----------

@dataclass
class Attachment:
    name: str
    url: str


import subprocess
import os
from typing import List

def call_copilot_for_code_generation(brief: str, checks: List[str], task_name: str, round_number: int) -> str:
    """
    Calls GitHub Copilot CLI to generate or update code based on the task brief, checks, and round.
    
    - For round 1 → generates a full static web app
    - For round >1 → updates existing code inside {task_name}/project using new attachments (assets/round_N)
    """

    print("🚀 Entered Copilot generation function")

    # Create base directory if needed
    base_dir = os.path.join(os.getcwd(), task_name)
    # project_dir = os.path.join(base_dir, "project")
    assets_dir = os.path.join(base_dir, "assets", f"round_{round_number}")

    os.makedirs(assets_dir, exist_ok=True)

    # Build the checklist description
    checking = ""
    for i, check in enumerate(checks, 1):
        checking += f"{i}. {check}, "

    # --- Prompt logic based on round ---
    if round_number == 1:
        prompt = f"""{brief}, create the html, css, js and only one professional readme.md so that it can be hosted on github page. your working directory is "./{task_name}" and for making this static web application assets are inside "./{task_name}/assets/round_{round_number}" and the important functionalities and requirements are in {checking}, make sure that you use only assets from given ones not self generated but the code should work with other samples when passed to hosted page. USERNAME IS {os.getenv("GITHUB_USERNAME")}. Dont forget to add LICENSE file with MIT license."""
    else:
        
        prompt = f"""You need to UPDATE the existing project which is inside ./{task_name} so first go through this code and understand. Refinements, updates and additional changes  are {brief} and the other important details about updates are {checking}, addtional attachments for updates are in ./{task_name}/assets/round_{round_number} so use them accordingly. Dont forget to update readme.md.Do NOT recreate from scratch; build upon existing implementation.Ensure backward compatibility — old assets and new ones must both work.USERNAME IS {GITHUB_USERNAME}."""



    print("🧠 Copilot Prompt:")
    print(prompt)

    # Run Copilot CLI
    command = [
        "npx",
        "-y",
        "@github/copilot",
        "--allow-all-tools",
        "-p",
        prompt
    ]

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            encoding="utf-8",
            text=True,
            cwd=base_dir  # Run inside task folder
        )

        print("STDOUT:\n", result.stdout)
        if result.stderr:
            print("STDERR:\n", result.stderr)

        if result.returncode != 0:
            raise Exception(f"Copilot CLI failed (exit {result.returncode})")

        print("✅ Copilot command completed successfully.")
        return result.stdout.strip()

    except Exception as e:
        print(f"❌ Error calling Copilot: {e}")
        return f"Error: {e}"


    except subprocess.CalledProcessError as e:
        print(f"Error calling Copilot: {e}")
        print(f"Stderr: {e.stderr}")
        raise Exception(f"Copilot execution failed: {e.stderr}")
    except subprocess.TimeoutExpired:
        raise Exception("Copilot command timed out")
    except Exception as e:
        raise Exception(f"Unexpected error calling Copilot: {str(e)}")


# ---------- Sample JSON Input ----------

task_json = """
{
  "email": "student@example.com",
  "secret": "my-secret",
  "task": "captcha-solver-001",
  "round": 2,
  "nonce": "ab12-xyz",
  "brief": "it should handle svg also passed by ?url=www.keshav.com/captcha.svg. Default to attached sample.",
  "checks": [
    
    "README.md is updated",
    "Page displays both default images png and svg as passed in attachments",
    "Page displays solved captchas text within 15 seconds"
  ],
  "evaluation_url": "https://example.com/notify",
  "attachments": [{ "name": "sample.svg", "url": "data:image/svg;base64,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" }]
}
"""

# ---------- Run the function ----------
import os
import base64
import re

import os
import re
import base64

def save_attachments(attachments, task_name, round_number):
    """
    Saves all attachments into a folder structure based on task and round.
    
    Structure:
      project_root/
        └── {task_name}/
              ├── assets/
              │     ├── round_1/
              │     ├── round_2/
              │     └── ...
              └── other files...
    
    - For round 1: creates a new folder with task_name (fresh start)
    - For round >1: reuses existing task folder and adds assets/round_{n}
    """

    # Define main task directory and round-specific asset directory
    base_dir = os.path.join(os.getcwd(), task_name)
    assets_dir = os.path.join(base_dir, "assets", f"round_{round_number}")

    # If round 1, recreate the base folder from scratch
    if round_number == 1:
        if os.path.exists(base_dir):
            import shutil
            shutil.rmtree(base_dir)  # Clean old data
        os.makedirs(assets_dir, exist_ok=True)
    else:
        os.makedirs(assets_dir, exist_ok=True)

    print(f"📁 Saving attachments for task '{task_name}', round {round_number}")
    print(f"➡️ Target folder: {assets_dir}")

    for att in attachments:
        # Expecting a structure like: {"name": "...", "url": "data:image/png;base64,..."}
        url = att.get("url") if isinstance(att, dict) else getattr(att, "url", None)
        name = att.get("name") if isinstance(att, dict) else getattr(att, "name", None)

        if not url or not name:
            print(f"⚠️ Skipping attachment: missing 'url' or 'name'")
            continue

        match = re.match(r"^data:(.*?);base64,(.*)$", url)
        if not match:
            print(f"⚠️ Skipping {name}: not a valid base64 data URI")
            continue

        mime_type, b64_data = match.groups()

        try:
            # Decode base64 content
            file_data = base64.b64decode(b64_data)

            # Create full output path
            file_path = os.path.join(assets_dir, name)

            # Write to file
            with open(file_path, "wb") as f:
                f.write(file_data)

            print(f"✅ Saved {name} ({mime_type}) to {file_path}")

        except Exception as e:
            print(f"❌ Failed to decode {name}: {e}")


import os
import subprocess
import requests
import base64

# ---------------------
# Configuration
# ---------------------
import os
from dotenv import load_dotenv


load_dotenv()


GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")

# Also ensure Copilot / git picks it up
os.environ["GITHUB_TOKEN"] = GITHUB_TOKEN
os.environ["GITHUB_USERNAME"] = GITHUB_USERNAME



import os
import subprocess
import requests


GITHUB_API = "https://api.github.com"


# ---------------------
# 1. Initialize local Git repository
# ---------------------
def init_local_git_repo(project_dir):
    if not os.path.exists(os.path.join(project_dir, ".git")):
        subprocess.run(["git", "init"], cwd=project_dir, check=True)
        print("✅ Initialized local Git repository")
    else:
        print("ℹ️ Git repository already exists")


# ---------------------
# 2. Create a new GitHub repository
# ---------------------
def create_github_repo(repo_name):
    url = f"{GITHUB_API}/user/repos"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "name": repo_name,
        "description": "Automatically generated project with MIT license",
        "private": False,
        "has_issues": True,
        "has_projects": False,
        "has_wiki": False
    }
    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()
    html_url = response.json()["html_url"]
    print(f"✅ GitHub repository created: {html_url}")
    return html_url


# ---------------------
# 3. Add all files and commit
# ---------------------
def commit_all_files(project_dir, message="Update project"):
    subprocess.run(["git", "add", "."], cwd=project_dir, check=True)
    subprocess.run(["git", "commit", "-m", message], cwd=project_dir, check=True)

    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=project_dir,
        capture_output=True,
        text=True,
        check=True
    )
    sha = result.stdout.strip()
    print(f"✅ Commit created: {sha}")
    return sha


# ---------------------
# 4. Add remote and push to GitHub
# ---------------------
def push_to_github(project_dir, repo_name):
    remote_url = f"https://{GITHUB_USERNAME}:{GITHUB_TOKEN}@github.com/{GITHUB_USERNAME}/{repo_name}.git"

    # Add remote (ignore if already exists)
    subprocess.run(["git", "remote", "remove", "origin"], cwd=project_dir, check=False)
    subprocess.run(["git", "remote", "add", "origin", remote_url], cwd=project_dir, check=False)

    # Push to main
    subprocess.run(["git", "branch", "-M", "main"], cwd=project_dir, check=True)
    subprocess.run(["git", "push", "-u", "origin", "main"], cwd=project_dir, check=True)
    print("✅ Pushed to GitHub")


# ---------------------
# 5. Enable GitHub Pages
# ---------------------
def enable_github_pages(repo_name):
    url = f"{GITHUB_API}/repos/{GITHUB_USERNAME}/{repo_name}/pages"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "source": {"branch": "main", "path": "/"},
        "build_type": "legacy"
    }
    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()
    print("🌍 GitHub Pages enabled!")
    return f"https://{GITHUB_USERNAME}.github.io/{repo_name}/"


# ---------------------
# 7. Full pipeline (round-aware)
# ---------------------
def push(REPO_NAME, round_number):
    """
    For round 1: initialize repo, create remote, first commit, push, and enable Pages.
    For round >1: only commit latest changes and push to existing repo.
    """

    # Define repo directory
    project_dir = os.path.join(os.getcwd(), REPO_NAME)

    if round_number == 1:
        print(f"🚀 Round 1 detected: initializing new GitHub repository for '{REPO_NAME}'")

        # 1. Init local git
        init_local_git_repo(project_dir)

        # 2. Create GitHub repo
        repo_url = create_github_repo(REPO_NAME)

        # 3. Initial commit
        commit_message = f"Initial commit for round {round_number} with LICENSE and base code"
        commit_sha = commit_all_files(project_dir, message=commit_message)

        # 4. Push to GitHub
        push_to_github(project_dir, REPO_NAME)

        # 5. Enable GitHub Pages
        site_url = enable_github_pages(REPO_NAME)

    else:
        print(f"🔁 Round {round_number} detected: committing updates to existing repo '{REPO_NAME}'")

        # Ensure repo exists locally
        if not os.path.exists(os.path.join(project_dir, ".git")):
            raise Exception("❌ No local git repository found. Did you run round 1 first?")

        # 1. Commit updates
        commit_message = f"Update project for round {round_number} (new assets and features)"
        try:
            commit_sha = commit_all_files(project_dir, message=commit_message)
        except subprocess.CalledProcessError:
            print("⚠️ No changes to commit, skipping.")
            commit_sha = None

        # 2. Push updates
        subprocess.run(["git", "push"], cwd=project_dir, check=True)
        print("✅ Updated changes pushed successfully.")

        # 3. Reuse previous URLs
        repo_url = f"https://github.com/{GITHUB_USERNAME}/{REPO_NAME}"
        site_url = f"https://{GITHUB_USERNAME}.github.io/{REPO_NAME}/"

    return repo_url, commit_sha, site_url


    
def run_check(data: dict):
    """Run the same logic as the main block but return results."""
    attachments = [Attachment(**a) for a in data.get("attachments", [])]

    save_attachments(attachments, data["task"], data["round"])
    print(data["brief"])
    print("🚀 Starting GitHub Copilot code generation...")

    try:
        output = call_copilot_for_code_generation(
            brief=data["brief"],
            checks=data["checks"],
            task_name=data["task"],
            round_number=data["round"]
        )
        print("✅ Copilot Output:")
        print(output)
    except Exception as e:
        print("❌ Error during Copilot generation:")
        print(e)

    repo_url, commit_sha, site_url = push(data["task"], data["round"])
    print(repo_url, commit_sha, site_url)
    return repo_url, commit_sha, site_url


if __name__ == "__main__":
    # Existing main logic remains for CLI use
    data = json.loads(task_json)
    run_check(data)

    

