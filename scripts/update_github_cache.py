#!/usr/bin/env python3
import os, sys, json, urllib.request, datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LANDING_DIR = os.path.dirname(SCRIPT_DIR)
CACHE_FILE = os.path.join(LANDING_DIR, "projects_cache.json")
WORKSPACE_DIR = os.path.dirname(LANDING_DIR)

GITHUB_ORG = "semcod"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

def fetch_github_repo_info(repo_id):
    url = f"https://api.github.com/repos/{GITHUB_ORG}/{repo_id}"
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "Semcod Engine-CacheUpdater/1.0")
    if GITHUB_TOKEN:
        req.add_header("Authorization", f"token {GITHUB_TOKEN}")
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode('utf-8'))
                return {
                    'stars': data.get('stargazers_count', 0),
                    'forks': data.get('forks_count', 0),
                    'issues': data.get('open_issues_count', 0),
                    'language': data.get('language') or 'Python',
                    'updated_at': data.get('updated_at', '')
                }
    except Exception as e:
        print(f"[Warning] Cannot fetch live GitHub stats for {repo_id}: {e}")
    return None

def update_cache():
    if not os.path.exists(CACHE_FILE):
        sys.exit(1)
    with open(CACHE_FILE, 'r', encoding='utf-8') as f:
        cache_data = json.load(f)
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    for proj_id, proj in cache_data.get('projects', {}).items():
        local_readme = os.path.join(WORKSPACE_DIR, proj_id, "README.md")
        if os.path.exists(local_readme):
            with open(local_readme, 'r', encoding='utf-8', errors='ignore') as rf:
                proj['readme'] = rf.read()
        gh_info = fetch_github_repo_info(proj_id)
        if gh_info:
            proj['stars'] = gh_info['stars']
            proj['forks'] = gh_info['forks']
            proj['issues'] = gh_info['issues']
            proj['language'] = gh_info['language']
            proj['last_commit'] = gh_info['updated_at']

    cache_data['last_updated'] = now_iso
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache_data, f, indent=2, ensure_ascii=False)
    print(f"[Success] Updated cache for semcod.")

if __name__ == '__main__':
    update_cache()
