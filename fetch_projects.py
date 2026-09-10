import json
import os
import sys
import time
from typing import Optional
import requests

DEFAULT_PROJECT_ID = "1555157"
OUTPUT_FILE = "projects.json"
REQUEST_TIMEOUT = 15

def get_api_key() -> str:
    key = os.environ.get("CURSEFORGE_API_KEY")
    if not key:
        sys.exit("ERROR: CURSEFORGE_API_KEY environment variable is not set.")
    return key

def fetch_project(project_id: int, api_key: str) -> Optional[dict]:
    headers = {
        "x-api-key": api_key,
        "Accept": "application/json",
    }
    
    urls = [
        f"https://curseforge.com{project_id}",
        f"https://curseforge.com{project_id}",
        f"https://curseforge.com{project_id}"
    ]
    
    payload = {}
    for url in urls:
        try:
            response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
            if response.status_code == 200:
                payload = response.json().get("data") or {}
                if payload:
                    print(f"  ✓ Success using endpoint: {url}")
                    break
        except requests.RequestException:
            continue

    if not payload:
        print(f"  ! Skipped project {project_id}: Checked all CurseForge sub-endpoints but data payload returned empty.")
        return None

    name = payload.get("name", "Untitled project")
    summary = payload.get("summary", "")
    
    logo = payload.get("logo") or {}
    logo_url = logo.get("url") or logo.get("thumbnailUrl") or ""
    
    links = payload.get("links") or {}
    website_url = links.get("websiteUrl") or f"https://www.curseforge.com/minecraft-bedrock/maps/backrooms-back-on-track"

    return {
        "name": name,
        "summary": summary,
        "logoUrl": logo_url,
        "websiteUrl": website_url,
    }

def main() -> None:
    api_key = get_api_key()
    
    raw_input = os.environ.get("PROJECT_IDS")
    if not raw_input or raw_input.strip() == "":
        raw_input = DEFAULT_PROJECT_ID

    project_ids = []
    for item in raw_input.split(","):
        item = item.strip()
        if item.isdigit():
            project_ids.append(int(item))

    if not project_ids:
        project_ids = [int(DEFAULT_PROJECT_ID)]

    projects = []
    print(f"Connecting to CurseForge API to query {len(project_ids)} target project(s)...")
    
    for project_id in project_ids:
        print(f"→ Processing ID: {project_id}")
        data = fetch_project(project_id, api_key)
        if data:
            projects.append(data)
            print(f"  ✓ Successfully extracted data for: {data['name']}")
        time.sleep(0.3)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(projects, f, indent=2, ensure_ascii=False)

    print(f"Pipeline complete. Wrote {len(projects)} record(s) to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
