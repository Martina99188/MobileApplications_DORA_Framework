import pandas as pd
import matplotlib.pyplot as plt

# =========================
# FILES
# =========================
INPUT_FILE = "./DORA_Metrics/CLT_days.csv"
OUTPUT_FILE = "/extracted_data/CLT_days_classified.csv"
PLOT_FILE_COMMITS = "./extracted_data/clt_commits_distribution.png"
PLOT_FILE_REPOS = "./extracted_data/clt_repos_distribution.png"

# =========================
# LOAD DATA
# =========================
df = pd.read_csv(
    INPUT_FILE,
    sep=',',
    names=['RepositoryName','CommitId','CommitDatetime',
           'FirstReleaseBeforeCommit','ReleaseBeforeDatetime',
           'MillisecondsBeforeCommit','FirstReleaseAfterCommit',
           'ReleaseAfterDatetime','MillisecondsAfterCommit'],
    skiprows=1,
    parse_dates=['CommitDatetime','ReleaseAfterDatetime']
)

# =========================
# CLT = (t_deploy - t_commit)
# =========================
df['lead_time_seconds'] = (
    df['ReleaseAfterDatetime'] - df['CommitDatetime']
).dt.total_seconds()

# Remove invalid values
df = df[df['lead_time_seconds'] > 0]

# Conversion to days
df['lead_time_days'] = df['lead_time_seconds'] / (60 * 60 * 24)

# =========================
# MEAN CLT (DORA)
# =========================
mean_clt = df['lead_time_days'].mean()

print("\n[INFO] Mean Lead Time for Changes (days):", mean_clt)

# =========================
# DORA CLASSIFICATION (INTERVALS)
# =========================
def classify_clt(days):
    if pd.isna(days):
        return None
    if days < 1/24:          # < 1 hour
        return "Elite"
    elif days < 7:           # < 1 week (include 1 day–1 week)
        return "High"
    elif days <= 180:        # 1–6 months
        return "Medium"
    else:
        return "Low"

ordered_levels = ["Elite","High","Medium","Low"]

# =========================
# COMMIT-LEVEL (DORA)
# =========================
df['clt_level'] = df['lead_time_days'].apply(classify_clt)

level_counts_commits = (
    df['clt_level']
    .value_counts()
    .reindex(ordered_levels, fill_value=0)
)

plt.figure(figsize=(8,6))
level_counts_commits.plot(kind="bar")

plt.title("Changes Lead Time (Commit-level)")
plt.xlabel("Performance Level")
plt.ylabel("Number of Commits")
plt.xticks(rotation=0)

for i, val in enumerate(level_counts_commits):
    plt.text(i, val + max(level_counts_commits)*0.01, str(val), ha='center')

plt.tight_layout()
plt.savefig(PLOT_FILE_COMMITS)
plt.show()

# =========================
# REPOSITORY-LEVEL (FURTHER ANALYSIS)
# =========================
median_per_repo = (
    df.groupby('RepositoryName')['lead_time_days']
    .median()
    .reset_index()
)

median_per_repo['clt_level'] = median_per_repo['lead_time_days'].apply(classify_clt)

level_counts_repo = (
    median_per_repo['clt_level']
    .value_counts()
    .reindex(ordered_levels, fill_value=0)
)

plt.figure(figsize=(8,6))
level_counts_repo.plot(kind="bar")

plt.title("Changes Lead Time (Repository-level)")
plt.xlabel("Performance Level")
plt.ylabel("Number of Repositories")
plt.xticks(rotation=0)

for i, val in enumerate(level_counts_repo):
    plt.text(i, val + max(level_counts_repo)*0.01, str(val), ha='center')

plt.tight_layout()
plt.savefig(PLOT_FILE_REPOS)
plt.show()

# =========================
# SAVE OUTPUT
# =========================
df.to_csv(OUTPUT_FILE, index=False)

print(f"\n[INFO] Classified CSV saved in {OUTPUT_FILE}")