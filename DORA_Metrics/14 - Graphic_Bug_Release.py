import pandas as pd
import matplotlib.pyplot as plt

# =========================
# FILES
# =========================
INPUT_FILE = "./extracted_data/change_failure_rate.csv"
OUTPUT_FILE = "./extracted_data/change_failure_rate_classified.csv"
PLOT_FILE = "./extracted_data/cfr_distribution.png"

# =========================
# LOAD DATA
# =========================
df = pd.read_csv(INPUT_FILE)

# =========================
# CLEAN DATA
# =========================
# Remove zero or negative values
df = df[df["change_failure_rate_percent"].notna()]
df = df[df["change_failure_rate_percent"] >= 0]

# =========================
# DORA CLASSIFICATION
# =========================
def classify_cfr(val):
    if pd.isna(val):
        return None
    if val <= 15:
        return "Elite"       # 0–15%
    elif val <= 30:
        return "High"        # 16–30%
    elif val <= 45:
        return "Medium"      # 31–45%
    else:
        return "Low"         # >45%

ordered_levels = ["Elite", "High", "Medium", "Low"]

df["cfr_level"] = df["change_failure_rate_percent"].apply(classify_cfr)

# =========================
# DEBUG STATS
# =========================
print("\n[INFO] CFR statistics:")
print(df["change_failure_rate_percent"].describe())

print("\n[INFO] CFR distribution:")
print(df["cfr_level"].value_counts())

# =========================
# SAVE CSV
# =========================
df.to_csv(OUTPUT_FILE, index=False)
print(f"\n[INFO] Classified CSV saved in {OUTPUT_FILE}")

# =========================
# PLOT DISTRIBUTION
# =========================
level_counts = (
    df["cfr_level"]
    .value_counts()
    .reindex(ordered_levels, fill_value=0)
)

plt.figure(figsize=(8,6))
level_counts.plot(kind="bar")

plt.title("Change Failure Rate")
plt.xlabel("Performance Level")
plt.ylabel("Number of Repositories")
plt.xticks(rotation=0)

# Labels above the bars
for i, val in enumerate(level_counts):
    plt.text(i, val + max(level_counts)*0.01, str(val), ha='center')

plt.tight_layout()
plt.savefig(PLOT_FILE)
plt.show()

print(f"[INFO] Plot saved in {PLOT_FILE}")