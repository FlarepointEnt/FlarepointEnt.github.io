#!/usr/bin/env python3
"""
fetch_projects.py — FlarepointEnt automation brain.

Pulls live project data from the CurseForge API and writes it to
projects.json, which index.html fetches at page load to build the
project cards. Run by .github/workflows/update_projects.yml on a
schedule, or manually:

    CURSEFORGE_API_KEY=your_key python3 fetch_projects.py

The API key is read from an environment variable only. It is never
hardcoded here and never committed to the repository — in CI it is
injected from a GitHub Actions secret.
"""

import json
import os
import sys
import time
from typing import Optional

import requests

# ---------------------------------------------------------------------------
# Add your CurseForge project (mod) IDs here.
# Find a project's ID on its CurseForge page, in the "About Project"
# panel on the right-hand side (it's a plain number, e.g. 123456).
# ---------------------------------------------------------------------------
PROJECT_IDS = [
    123456,  # TODO: replace with Dead Static's real CurseForge ID
    234567,  # TODO: replace with Hollow Signal's real CurseForge ID
    345678,  # TODO: replace with The Undertow's real CurseForge ID
]

API_BASE = "https://api.curseforge.com/v1/mods"
OUTPUT_FILE = "projects.json"
REQUEST_TIMEOUT = 15  # seconds


def get_api_key() -> str:
    key = os.environ.get("CURSEFORGE_API_KEY")
    if not key:
        sys.exit(
            "ERROR: CURSEFORGE_API_KEY is not set.\n"
            "Set it as an environment variable locally, or as a GitHub "
            "Actions secret in CI, before running this script."
        )
    return key


def fetch_project(project_id: int, api_key: str) -> Optional[dict]:
    url = f"{API_BASE}/{project_id}"
    headers = {
        "x-api-key": api_key,
        "Accept": "application/json",
    }
    try:
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as exc:
        print(f"  ! Skipped project {project_id}: {exc}")
        return None

    payload = response.json().get("data") or {}
    if not payload:
        print(f"  ! Skipped project {project_id}: empty response")
        return None

    logo = payload.get("logo") or {}
    links = payload.get("links") or {}

    return {
        "name": payload.get("name", "Untitled project"),
        "summary": payload.get("summary", ""),
        "logoUrl": logo.get("url", ""),
        "websiteUrl": links.get("websiteUrl", ""),
    }


def main() -> None:
    api_key = get_api_key()
    projects = []

    print(f"Fetching {len(PROJECT_IDS)} project(s) from CurseForge...")
    for project_id in PROJECT_IDS:
        print(f"→ {project_id}")
        data = fetch_project(project_id, api_key)
        if data:
            projects.append(data)
        time.sleep(0.3)  # be polite to the API

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(projects, f, indent=2, ensure_ascii=False)

    print(f"Wrote {len(projects)} project(s) to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
