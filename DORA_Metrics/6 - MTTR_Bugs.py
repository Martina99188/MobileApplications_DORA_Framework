import pandas as pd

BUGS_CSV = "./extracted_data/bugs_all.csv"
OUTPUT_FILE = "./extracted_data/mttr_bugs.csv"

bugs_df = pd.read_csv(BUGS_CSV, parse_dates=["created_at", "closed_at"])

closed_bugs = bugs_df.dropna(subset=["closed_at"]).copy()

closed_bugs = closed_bugs[~closed_bugs["labels"].str.contains("R: invalid / not a bug", na=False)]

closed_bugs["recovery_hours"] = (closed_bugs["closed_at"] - closed_bugs["created_at"]).dt.total_seconds() / 3600

mttr_per_repo = (
    closed_bugs.groupby("repository")["recovery_hours"]
    .mean()
    .reset_index()
)
mttr_per_repo.rename(columns={"recovery_hours": "mttr_hours"}, inplace=True)

mttr_per_repo.to_csv(OUTPUT_FILE, index=False)
print(f"[INFO] MTTR bug saved in {OUTPUT_FILE}")
