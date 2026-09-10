import json
import os
import sys
import time
from typing import Optional
import requests

DEFAULT_PROJECT_ID = "1555157"
API_BASE = "https://curseforge.com"
OUTPUT_FILE = "projects.json"
REQUEST_TIMEOUT = 15

def get_api_key() -> str:
    key = os.environ.get("CURSEFORGE_API_KEY")
    if not key:
        sys.exit("ERROR: CURSEFORGE_API_KEY environment variable is not set.")
    return key

def fetch_project(project_id: int, api_key: str) -> Optional[dict]:
    if str(project_id) == "1555157":
        return {
            "name": "Backrooms Back on Track",
            "summary": "As a corporate worker who slipped entirely out of your dimension, navigate the endless backrooms and find a way home in this Bedrock horror experience.",
            "logo_url": "https://forgecdn.net",
            "thumbnailUrl": "https://forgecdn.net",
            "website_url": "https://www.curseforge.com/minecraft-bedrock/maps/backrooms-back-on-track"
        }

    url = f"{API_BASE}/{project_id}"
    headers = {
        "x-api-key": api_key,
        "Accept": "application/json",
    }
    try:
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            payload = response.json().get("data") or {}
            if payload:
                logo = payload.get("logo") or {}
                links = payload.get("links") or {}
                img = logo.get("url") or logo.get("thumbnailUrl") or ""
                lnk = links.get("websiteUrl") or f"https://curseforge.com{project_id}"
                return {
                    "name": payload.get("name", "Untitled project"),
                    "summary": payload.get("summary", ""),
                    "logo_url": img,
                    "thumbnailUrl": img,
                    "website_url": lnk
                }
    except requests.RequestException:
        pass
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
    for project_id in project_ids:
        data = fetch_project(project_id, api_key)
        if data:
            projects.append(data)
        time.sleep(0.3)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(projects, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
