#!/usr/bin/env python3
"""
fetch_projects.py — FlarepointEnt automation brain.
 
Pulls live project data from the CurseForge API and writes it to
projects.json, which index.html fetches at page load to build the
project cards. Run by .github/workflows/update_projects.yml on a
schedule or on-demand — no hardcoded list of IDs to keep in sync
with this file.
 
Project IDs come from (in priority order):
  1. A command-line argument:      python fetch_projects.py "1555157,123456"
  2. The PROJECT_IDS env var:      PROJECT_IDS="1555157,123456" python fetch_projects.py
  3. DEFAULT_PROJECT_IDS below, if neither of the above is set.
 
In CI, the workflow's "project_ids" workflow_dispatch input is passed
in as the PROJECT_IDS env var. Scheduled (cron) runs don't carry that
input, so they fall back to DEFAULT_PROJECT_IDS automatically — the
site never goes stale-blank just because nobody typed anything in.
 
The CurseForge API key is read from an environment variable only. It
is never hardcoded here and never committed to the repository — in CI
it is injected from a GitHub Actions secret.
"""
 
import json
import os
import sys
import time
from typing import List, Optional
 
import requests
 
# Fallback used whenever no project IDs are supplied any other way.
# Keep this in sync with the workflow's default workflow_dispatch input.
DEFAULT_PROJECT_IDS = "1555157"
 
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
 
 
def resolve_project_ids() -> List[int]:
    """
    Work out which CurseForge project IDs to fetch, from a CLI arg,
    then the PROJECT_IDS env var, then DEFAULT_PROJECT_IDS — parsing
    a comma-separated string into a clean list of ints along the way.
    """
    if len(sys.argv) > 1 and sys.argv[1].strip():
        raw = sys.argv[1]
        source = "command-line argument"
    else:
        raw = os.environ.get("PROJECT_IDS", "")
        source = "PROJECT_IDS environment variable"
 
    raw = raw.strip()
    if not raw:
        raw = DEFAULT_PROJECT_IDS
        source = "default fallback"
 
    print(f"Project IDs source: {source} ('{raw}')")
 
    ids: List[int] = []
    for chunk in raw.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        try:
            ids.append(int(chunk))
        except ValueError:
            print(f"  ! Ignoring invalid project ID: '{chunk}'")
 
    if not ids:
        print(f"No valid project IDs found — falling back to default: {DEFAULT_PROJECT_IDS}")
        ids = [int(pid) for pid in DEFAULT_PROJECT_IDS.split(",") if pid.strip()]
 
    return ids
 
 
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
    project_ids = resolve_project_ids()
    projects = []
 
    print(f"Fetching {len(project_ids)} project(s) from CurseForge...")
    for project_id in project_ids:
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
 
