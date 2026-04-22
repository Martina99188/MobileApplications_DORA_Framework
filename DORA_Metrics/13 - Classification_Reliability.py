import pandas as pd

INPUT_FILE = "./extracted_data/reliability_metrics.csv"
OUTPUT_FILE = "./extracted_data/reliability_classified.csv"

df = pd.read_csv(INPUT_FILE)


# =========================
# Availability
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


# =========================
# Error Rate
# =========================
def classify_error_rate(val):
    if pd.isna(val):
        return None

    val_pct = val * 100

    if val_pct < 0.1:
        return "Elite"
    elif val_pct < 0.5:
        return "High"
    elif val_pct < 1.0:
        return "Medium"
    else:
        return "Low"


# =========================
# MTBF (hours → days)
# =========================
def classify_mtbf(hours):
    if pd.isna(hours):
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
# Apply classifications
# =========================
df["availability_level"] = df["availability"].apply(classify_availability)

df["bug_error_rate_level"] = df["bug_error_rate"].apply(classify_error_rate)

df["build_error_rate_level"] = df["build_error_rate"].apply(classify_error_rate)

df["mtbf_level"] = df["mtbf_hours"].apply(classify_mtbf)


df.to_csv(OUTPUT_FILE, index=False)

print(f"[INFO] Reliability classification saved in {OUTPUT_FILE}")