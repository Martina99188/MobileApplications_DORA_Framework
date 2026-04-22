import pandas as pd
import requests
from pathlib import Path
import time
import math

INPUT_REPOS_CSV = "./extracted_data/repositories_full.csv"
OUTPUT_DIR = "./extracted_data"
GITHUB_TOKEN = "" # put the GitHub token

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

PER_PAGE = 100
DELAY = 0.5
BATCH_SIZE = 50        # How many repositories per file
START_BATCH = 0        # to resume from a specific batch
MAX_RETRIES = 3        # Maximum number of retries for connection errors
RETRY_DELAY = 5        # seconds between retries

def get_issues(owner, repo):
    issues = []
    page = 1
    while True:
        url = f"https://api.github.com/repos/{owner}/{repo}/issues"
        params = {"state": "all", "per_page": PER_PAGE, "page": page}

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = requests.get(url, headers=HEADERS, params=params, timeout=20)
                break
            except requests.exceptions.RequestException as e:
                if attempt == MAX_RETRIES:
                    return issues
                time.sleep(RETRY_DELAY)

        if response.status_code != 200:
            return issues

        data = response.json()
        if not data:
            break

        data = [i for i in data if "pull_request" not in i]

        bug_issues = [i for i in data if any("bug" in l["name"].lower() for l in i.get("labels", []))]

        for i in bug_issues:
            issues.append({
                "repository": f"{owner}/{repo}",
                "issue_id": i["number"],
                "title": i["title"],
                "state": i["state"],
                "created_at": i["created_at"],
                "closed_at": i.get("closed_at"),
                "labels": ", ".join([l["name"] for l in i.get("labels", [])])
            })

        page += 1
        time.sleep(DELAY)

    return issues

def main():
    output_path = Path(OUTPUT_DIR)
    output_path.mkdir(parents=True, exist_ok=True)

    repos_df = pd.read_csv(INPUT_REPOS_CSV)

    repos_df["full_name"] = repos_df["full_name"].fillna("").astype(str).str.strip()

    valid_repos = [r for r in repos_df["full_name"] if r and "/" in r]
    invalid_repos = [r for r in repos_df["full_name"] if not r or "/" not in r]

    if invalid_repos:
        failed_file = output_path / "failed_repos.csv"
        pd.DataFrame(invalid_repos, columns=["full_name"]).to_csv(failed_file, index=False)

    total_batches = math.ceil(len(valid_repos) / BATCH_SIZE)

    for batch_idx in range(START_BATCH, total_batches):
        print(f"\n[INFO] Batch {batch_idx + 1}/{total_batches}")

        start = batch_idx * BATCH_SIZE
        end = start + BATCH_SIZE
        batch_repos = valid_repos[start:end]

        all_issues = []

        for repo_full in batch_repos:
            owner, repo = repo_full.split("/")
            print(f"[INFO]   → {owner}/{repo}")

            repo_issues = get_issues(owner, repo)
            all_issues.extend(repo_issues)

        if all_issues:
            batch_file = output_path / f"bugs_batch_{batch_idx:03d}.csv"
            pd.DataFrame(all_issues).to_csv(batch_file, index=False)
            print(f"[INFO] Saved: {batch_file}")
        else:
            print("[INFO] No bugs found in this batch")

        time.sleep(5) 

if __name__ == "__main__":
    main()
