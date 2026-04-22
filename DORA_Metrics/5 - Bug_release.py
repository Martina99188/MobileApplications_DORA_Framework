import pandas as pd
from pathlib import Path
import glob

RELEASE_CSV = "./extracted_data/releases_mapped.csv"
BUGS_BATCH_DIR = "./extracted_data"
OUTPUT_DIR = "./extracted_data"

BUGS_UNIFIED_FILE = "bugs_all.csv"
OUTPUT_FILE = "change_failure_rate.csv"

TOLERANCE_DAYS = 7

def main():
    output_path = Path(OUTPUT_DIR)
    output_path.mkdir(parents=True, exist_ok=True)


    releases_df = pd.read_csv(RELEASE_CSV, parse_dates=["release_date"])
    releases_df["release_date"] = releases_df["release_date"].dt.tz_localize(None)

    all_bug_files = sorted(glob.glob(f"{BUGS_BATCH_DIR}/bugs_batch_*.csv"))

    bugs_df_list = []
    for f in all_bug_files:
        df = pd.read_csv(f, parse_dates=["created_at", "closed_at"])
        df["created_at"] = df["created_at"].dt.tz_localize(None)
        df["closed_at"] = df["closed_at"].dt.tz_localize(None)
        bugs_df_list.append(df)

    bugs_df = pd.concat(bugs_df_list, ignore_index=True)

    bugs_df.drop_duplicates(subset=["repository", "issue_id"], inplace=True)

    unified_path = output_path / BUGS_UNIFIED_FILE
    bugs_df.to_csv(unified_path, index=False)

    print(f"[INFO] Consolidated bug report saved in {unified_path}")
    print(f"[INFO] Total consolidated bugs: {len(bugs_df)}")

    cfr_list = []

    for repo in releases_df["repository"].unique():
        repo_releases = releases_df[
            releases_df["repository"] == repo
        ].sort_values("release_date")

        repo_bugs = bugs_df[
            bugs_df["repository"] == repo
        ]

        total_releases = len(repo_releases)
        failed_releases = 0

        for _, row in repo_releases.iterrows():
            release_date = row["release_date"]
            start_window = release_date
            end_window = release_date + pd.Timedelta(days=TOLERANCE_DAYS)

            bugs_in_window = repo_bugs[
                (repo_bugs["created_at"] >= start_window) &
                (repo_bugs["created_at"] <= end_window)
            ]

            if len(bugs_in_window) > 0:
                failed_releases += 1

        cfr_percent = (
            (failed_releases / total_releases) * 100
            if total_releases > 0 else 0
        )

        cfr_list.append({
            "repository": repo,
            "total_releases": total_releases,
            "failed_releases": failed_releases,
            "change_failure_rate_percent": round(cfr_percent, 2)
        })

    cfr_df = pd.DataFrame(cfr_list)
    cfr_path = output_path / OUTPUT_FILE
    cfr_df.to_csv(cfr_path, index=False)

    print(f"[INFO] Change Failure Rate saved in {cfr_path}")


if __name__ == "__main__":
    main()
