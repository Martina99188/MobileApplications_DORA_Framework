import pandas as pd
import requests
from pathlib import Path
import time

INPUT_REPOS_CSV = "./extracted_data/repositories_full.csv"
OUTPUT_DIR = "./extracted_data"
OUTPUT_FILE = "build_logs.csv"

GITHUB_TOKEN = "" # put the GitHub token
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

PER_PAGE = 100
DELAY = 0.5  


def get_build_runs(owner, repo):
    runs = []
    page = 1
    while True:
        url = f"https://api.github.com/repos/{owner}/{repo}/actions/runs"
        params = {"per_page": PER_PAGE, "page": page}
        response = requests.get(url, headers=HEADERS, params=params)

        if response.status_code != 200:
            break

        data = response.json()
        workflow_runs = data.get("workflow_runs", [])
        if not workflow_runs:
            break

        for run in workflow_runs:
            runs.append({
                "repository": f"{owner}/{repo}",
                "workflow_name": run.get("name"),
                "run_id": run.get("id"),
                "status": run.get("status"),
                "conclusion": run.get("conclusion"),
                "created_at": run.get("created_at"),
                "updated_at": run.get("updated_at")
            })

        page += 1
        time.sleep(DELAY)

    return runs


def main():
    output_path = Path(OUTPUT_DIR)
    output_path.mkdir(parents=True, exist_ok=True)

    repos_df = pd.read_csv(INPUT_REPOS_CSV)
    all_runs = []

    for repo_full in repos_df["full_name"]:
        if pd.isna(repo_full) or "/" not in repo_full:
            continue

        owner, repo = repo_full.split("/")
        print(f"[INFO] Extract build runs from: {owner}/{repo}")
        repo_runs = get_build_runs(owner, repo)
        all_runs.extend(repo_runs)

    if all_runs:
        df = pd.DataFrame(all_runs)
        df.to_csv(output_path / OUTPUT_FILE, index=False)
        print(f"[INFO] Build logs saved in {output_path / OUTPUT_FILE}")
    else:
        print("[INFO] No build runs found.")

if __name__ == "__main__":
    main()
