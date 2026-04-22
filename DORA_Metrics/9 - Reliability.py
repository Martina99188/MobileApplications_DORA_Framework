import pandas as pd
from pathlib import Path

RELEASES_CSV = "./extracted_data/releases_mapped.csv"
BUGS_CSV = "./extracted_data/bugs_all.csv"
BUILDS_CSV = "./extracted_data/build_logs.csv"

OUTPUT_DIR = "./extracted_data"
OUTPUT_FILE = "reliability_metrics.csv"


def main():
    output_path = Path(OUTPUT_DIR)
    output_path.mkdir(parents=True, exist_ok=True)

    releases_df = pd.read_csv(RELEASES_CSV, parse_dates=["release_date"])
    bugs_df = pd.read_csv(BUGS_CSV, parse_dates=["created_at", "closed_at"])
    builds_df = pd.read_csv(BUILDS_CSV, parse_dates=["created_at"])

    results = []

    for repo in releases_df["repository"].unique():

        # =========================
        # FILTER PER REPO
        # =========================
        repo_releases = releases_df[
            releases_df["repository"] == repo
        ].sort_values("release_date")

        repo_bugs = bugs_df[
            bugs_df["repository"] == repo
        ]

        repo_builds = builds_df[
            builds_df["repository"] == repo
        ]

        total_releases = len(repo_releases)
        total_bugs = len(repo_bugs)
        total_builds = len(repo_builds)

        if total_releases < 2:
            continue

        # =========================
        # FIX STATUS BUILD
        # =========================
        repo_builds["conclusion_clean"] = (
            repo_builds["conclusion"]
            .astype(str)
            .str.lower()
            .str.strip()
        )

        failed_builds = repo_builds[
            repo_builds["conclusion"].astype(str).str.lower().isin([
                "failure", "failed", "error"
            ])
        ].shape[0]

        # =========================
        # TIME WINDOW
        # =========================
        period_total_hours = (
            repo_releases["release_date"].max() -
            repo_releases["release_date"].min()
        ).total_seconds() / 3600

        if period_total_hours <= 0:
            continue

        # =========================
        # DOWNTIME (BUGS)
        # =========================
        closed_bugs = repo_bugs.dropna(subset=["closed_at"]).copy()

        if len(closed_bugs) > 0:
            closed_bugs["downtime_hours"] = (
                (closed_bugs["closed_at"] - closed_bugs["created_at"])
                .dt.total_seconds() / 3600
            )
            total_downtime = closed_bugs["downtime_hours"].sum()
        else:
            total_downtime = 0

        # clamp (avoid negative availability)
        total_downtime = min(total_downtime, period_total_hours)

        # =========================
        # METRICS
        # =========================

        availability = (
            (period_total_hours - total_downtime)
            / period_total_hours
        )

        bug_error_rate = (
            total_bugs / total_releases
            if total_releases > 0 else 0
        )

        build_error_rate = (
            failed_builds / total_builds
            if total_builds > 0 else 0
        )

        total_failures = total_bugs + failed_builds

        mtbf = (
            period_total_hours / total_failures
            if total_failures > 0 else None
        )

        # =========================
        # SAVE
        # =========================
        results.append({
            "repository": repo,

            "T_total_hours": round(period_total_hours, 2),
            "T_downtime_hours": round(total_downtime, 2),

            "availability": round(availability * 100, 4),  # percentage

            "N_releases": total_releases,
            "N_bugs": total_bugs,
            "N_total_builds": total_builds,
            "N_failed_builds": failed_builds,

            "bug_error_rate": round(bug_error_rate, 6),
            "build_error_rate": round(build_error_rate, 6),

            "N_failures": total_failures,
            "mtbf_hours": round(mtbf, 2) if mtbf else None
        })

    # =========================
    # EXPORT
    # =========================
    output_file = output_path / OUTPUT_FILE
    pd.DataFrame(results).to_csv(output_file, index=False)

    print(f"[INFO] Saved in: {output_file}")


if __name__ == "__main__":
    main()