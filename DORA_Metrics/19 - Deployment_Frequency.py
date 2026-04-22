import pandas as pd
import matplotlib.pyplot as plt

INPUT_FILE = './DORA_Metrics/DF_release.csv'
OUTPUT_FILE = './extracted_data/deployment_frequency_classified.csv'
PLOT_FILE = './extracted_data/deployment_frequency_distribution.png'

df = pd.read_csv(INPUT_FILE, sep=',', names=['RepositoryName','NumOfReleases','ReleaseFrequencyDays'], skiprows=1)

# ----------------------------
# Deployment Frequency (DF) Classification
# ----------------------------
def classify_df(freq_days):
    if pd.isna(freq_days):
        return None
    if freq_days < 1:
        return "Elite"           # multiple per day / daily
    elif freq_days <= 30:
        return "High"            # weekly → monthly
    elif freq_days <= 180:
        return "Medium"          # monthly → 6 months
    else:
        return "Low"

df["df_level"] = df["ReleaseFrequencyDays"].apply(classify_df)

# Save sorted CSV
df.to_csv(OUTPUT_FILE, index=False)
print(f"[INFO] Classified Deployment Frequency saved in {OUTPUT_FILE}")

# ----------------------------
# Distribution chart
# ----------------------------
ordered_levels = ["Elite", "High", "Medium", "Low"]
level_counts = df["df_level"].value_counts().reindex(ordered_levels, fill_value=0)

plt.figure(figsize=(8,6))
level_counts.plot(kind="bar")

plt.title("Deployment Frequency Classification Distribution")
plt.xlabel("Performance Level")
plt.ylabel("Number of Repositories")
plt.xticks(rotation=0)

# Add values above the bars
for i, val in enumerate(level_counts):
    plt.text(i, val + 0.5, str(val), ha='center', va='bottom', fontsize=8)

plt.tight_layout()
plt.savefig(PLOT_FILE)
plt.show()
print(f"[INFO] Plot saved in {PLOT_FILE}")