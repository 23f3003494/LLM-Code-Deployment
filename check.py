import json
import os
from typing import List
from dataclasses import dataclass
import subprocess
import re
import requests
import base64
from dotenv import load_dotenv

@dataclass
class Attachment:
    name: str
    url: str

load_dotenv()


GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")

os.environ["GITHUB_TOKEN"] = GITHUB_TOKEN
os.environ["GITHUB_USERNAME"] = GITHUB_USERNAME
GITHUB_API = "https://api.github.com"


def call_copilot_for_code_generation(brief: str, checks: List[str], task_name: str, round_number: int) -> str:
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

def save_attachments(attachments, task_name, round_number):
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

def init_local_git_repo(project_dir):
    if not os.path.exists(os.path.join(project_dir, ".git")):
        subprocess.run(["git", "init"], cwd=project_dir, check=True)
        print("✅ Initialized local Git repository")
    else:
        print("ℹ️ Git repository already exists")

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

def push_to_github(project_dir, repo_name):
    remote_url = f"https://{GITHUB_USERNAME}:{GITHUB_TOKEN}@github.com/{GITHUB_USERNAME}/{repo_name}.git"

    # Add remote (ignore if already exists)
    subprocess.run(["git", "remote", "remove", "origin"], cwd=project_dir, check=False)
    subprocess.run(["git", "remote", "add", "origin", remote_url], cwd=project_dir, check=False)

    # Push to main
    subprocess.run(["git", "branch", "-M", "main"], cwd=project_dir, check=True)
    subprocess.run(["git", "push", "-u", "origin", "main"], cwd=project_dir, check=True)
    print("✅ Pushed to GitHub")

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

    


