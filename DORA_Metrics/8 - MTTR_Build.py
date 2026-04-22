import pandas as pd

BUILD_LOGS_CSV = "./extracted_data/build_logs.csv"
OUTPUT_FILE_BUILDS = "./extracted_data/mttr_builds.csv"

builds_df = pd.read_csv(
    BUILD_LOGS_CSV,
    parse_dates=["created_at", "updated_at"]
)

builds_df["created_at"] = builds_df["created_at"].dt.tz_localize(None)
builds_df["updated_at"] = builds_df["updated_at"].dt.tz_localize(None)

builds_df = builds_df[
    builds_df["workflow_name"].str.contains(
        "build|ci|test|gradle|pipeline",
        case=False,
        na=False
    )
]

failed_builds = builds_df[
    (builds_df["status"] == "completed") &
    (builds_df["conclusion"].notna()) &
    (builds_df["conclusion"] != "success")
].copy()

failed_builds["recovery_hours"] = (
    (failed_builds["updated_at"] - failed_builds["created_at"])
    .dt.total_seconds() / 3600
)

mttr_builds_per_repo = (
    failed_builds
    .groupby("repository")["recovery_hours"]
    .mean()
    .reset_index()
)

mttr_builds_per_repo.rename(
    columns={"recovery_hours": "mttr_build_hours"},
    inplace=True
)

mttr_builds_per_repo.to_csv(OUTPUT_FILE_BUILDS, index=False)

print(f"[INFO] MTTR build saved in {OUTPUT_FILE_BUILDS}")
