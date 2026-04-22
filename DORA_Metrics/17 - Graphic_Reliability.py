import pandas as pd
import matplotlib.pyplot as plt

INPUT_FILE = "./extracted_data/reliability_metrics.csv"
OUTPUT_FILE = "./extracted_data/reliability_classified.csv"

PLOT_AVAIL = "./extracted_data/availability_distribution.png"
PLOT_ERROR_BUG = "./extracted_data/bug_error_distribution.png"
PLOT_ERROR_BUILD = "./extracted_data/build_error_distribution.png"
PLOT_MTBF = "./extracted_data/mtbf_distribution.png"


# =========================
# LOAD
# =========================
df = pd.read_csv(INPUT_FILE)


# =========================
# DATA CLEANING
# =========================

# 1. Availability → clamp + conversion %
df["availability"] = df["availability"].clip(lower=0)
df["availability_percent"] = df["availability"] * 100

# 2. Error rate:
# bug_error_rate = bugs per release (NOT a percentage)
# we convert this into a normalised percentage (proxy)
df["bug_error_rate_pct"] = df["bug_error_rate"] / 100

# build_error_rate is already a ratio (0–1)
df["build_error_rate_pct"] = df["build_error_rate"]

# =========================
# CLASSIFIERS
# =========================

def classify_availability(val):
    if pd.isna(val):
        return None
    if val >= 99.9:
        return "Elite"
    elif val >= 99.5:
        return "High"
    elif val >= 99.0:
        return "Medium"
    else:
        return "Low"


def classify_error_rate(val):
    if pd.isna(val):
        return None
    if val < 0.001:      # 0.1%
        return "Elite"
    elif val < 0.005:    # 0.5%
        return "High"
    elif val < 0.01:     # 1%
        return "Medium"
    else:
        return "Low"


def classify_mtbf(hours):
    if pd.isna(hours) or hours == 0:
        return None

    days = hours / 24

    if days > 30:
        return "Elite"
    elif days >= 7:
        return "High"
    elif days >= 1:
        return "Medium"
    else:
        return "Low"


# =========================
# APPLY CLASSIFICATION
# =========================

df["availability_level"] = df["availability_percent"].apply(classify_availability)

df["bug_error_rate_level"] = df["bug_error_rate_pct"].apply(classify_error_rate)

df["build_error_rate_level"] = df["build_error_rate_pct"].apply(classify_error_rate)

df["mtbf_level"] = df["mtbf_hours"].apply(classify_mtbf)


# =========================
# SAVE CSV
# =========================
df.to_csv(OUTPUT_FILE, index=False)
print(f"[INFO] Salvato CSV: {OUTPUT_FILE}")


# =========================
# PLOT FUNCTION
# =========================
def plot_distribution(series, title, output_file):
    order = ["Elite", "High", "Medium", "Low"]

    counts = (
        series.dropna()
        .value_counts()
        .reindex(order, fill_value=0)
    )

    plt.figure()
    ax = counts.plot(kind="bar")

    plt.title(title)
    plt.xlabel("Performance Level")
    plt.ylabel("Number of Repositories")

    # =========================
    # ADDING VALUES ABOVE THE BARS
    # =========================
    for i, value in enumerate(counts):
        ax.text(
            i,                  # position x
            value + 0.1,        # position y
            str(value),         # text
            ha='center',
            va='bottom'
        )

    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()
    
    
# =========================
# PLOTS
# =========================

plot_distribution(
    df["availability_level"],
    "Availability Proxy",
    PLOT_AVAIL
)

plot_distribution(
    df["bug_error_rate_level"],
    "Error Rate (Bug)",
    PLOT_ERROR_BUG
)

plot_distribution(
    df["build_error_rate_level"],
    "Error Rate (Build)",
    PLOT_ERROR_BUILD
)

plot_distribution(
    df["mtbf_level"],
    "Mean Time Between Failures",
    PLOT_MTBF
)

print("[INFO] Saved charts")