import pandas as pd
import matplotlib.pyplot as plt

# =========================
# FILES
# =========================
INPUT_FILE = "./extracted_data/mttr_bugs.csv"
OUTPUT_FILE = "./extracted_data/mttr_bugs_classified.csv"
PLOT_FILE = "./extracted_data/mttr_bugs_distribution.png"

# =========================
# LOAD DATA
# =========================
df = pd.read_csv(INPUT_FILE)

# Basic cleaning
df = df[df["mttr_hours"].notna()]
df = df[df["mttr_hours"] >= 0]

# =========================
# DORA MTTR RANKING
# =========================
def classify_mttr(hours):
    if hours < 1:
        return "Elite"
    elif hours < 24:
        return "High"
    elif hours <= 168:   # 7 days
        return "Medium"
    else:
        return "Low"

ordered_levels = ["Elite", "High", "Medium", "Low"]

df["mttr_level"] = df["mttr_hours"].apply(classify_mttr)

# Debug
print("\n[INFO] MTTR Bugs distribution:")
print(df["mttr_level"].value_counts())

# Save
df.to_csv(OUTPUT_FILE, index=False)

# =========================
# PLOT
# =========================
level_counts = df["mttr_level"].value_counts().reindex(ordered_levels, fill_value=0)

plt.figure(figsize=(8,6))
level_counts.plot(kind="bar")

plt.title("Failed Deployment Recovery Time (Bug)")
plt.xlabel("Performance Level")
plt.ylabel("Number of Repositories")
plt.xticks(rotation=0)

for i, val in enumerate(level_counts):
    plt.text(i, val + max(level_counts)*0.01, str(val), ha='center')

plt.tight_layout()
plt.savefig(PLOT_FILE)
plt.show()