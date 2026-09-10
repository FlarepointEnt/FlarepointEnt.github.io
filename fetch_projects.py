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
    
    url = f"https://curseforge.com{project_id}"
    
    try:
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        print(f"API Debug Status for ID {project_id}: {response.status_code}")
        
        if response.status_code == 200:
            payload = response.json().get("data") or {}
            if payload:
                name = payload.get("name", "Untitled project")
                summary = payload.get("summary", "")
                
                logo = payload.get("logo") or {}
                img = logo.get("url") or logo.get("thumbnailUrl") or ""
                
                links = payload.get("links") or {}
                lnk = links.get("websiteUrl") or f"https://curseforge.com{project_id}"
                
                return {
                    "name": name,
                    "summary": summary,
                    "logoUrl": img,
                    "logo_url": img,
                    "thumbnailUrl": img,
                    "websiteUrl": lnk,
                    "website_url": lnk
                }
    except requests.RequestException as e:
        print(f"Error connecting: {e}")
        
    return None

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
    print(f"Querying live CurseForge database for IDs: {project_ids}")
    
    for project_id in project_ids:
        data = fetch_project(project_id, api_key)
        if data:
            projects.append(data)
            print(f"Successfully scraped: {data['name']}")
        time.sleep(0.3)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(projects, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
