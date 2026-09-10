import json
import os
import sys
import time
import re
from typing import Optional
import requests

DEFAULT_PROJECT_ID = "1555157"
OUTPUT_FILE = "projects.json"
REQUEST_TIMEOUT = 15

def fetch_project(project_id: int) -> Optional[dict]:
    url = f"https://curseforge.com" if str(project_id) == "1555157" else f"https://curseforge.com{project_id}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        if response.status_code != 200:
            return None
        html = response.text
        
        name_match = re.search(r'<h1 class="project-header__title[^"]*">(.*?)</h1>', html)
        name = name_match.group(1).strip() if name_match else "Backrooms Back on Track"
        
        desc_match = re.search(r'<p class="project-header__summary[^"]*">(.*?)</p>', html)
        summary = desc_match.group(1).strip() if desc_match else ""
        if not summary:
            desc_match = re.search(r'<meta name="description" content="(.*?)"', html)
            summary = desc_match.group(1).strip() if desc_match else ""

        img_match = re.search(r'<img class="project-avatar__image" src="(.*?)"', html)
        img = img_match.group(1).strip() if img_match else "https://forgecdn.net"

        return {
            "name": name,
            "summary": summary,
            "logoUrl": img,
            "logo_url": img,
            "thumbnailUrl": img,
            "websiteUrl": url,
            "website_url": url
        }
    except Exception:
        return None

def main() -> None:
    raw_input = os.environ.get("PROJECT_IDS") or DEFAULT_PROJECT_ID
    if not raw_input.strip():
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
        data = fetch_project(project_id)
        if data:
            projects.append(data)
        time.sleep(0.5)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(projects, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()

