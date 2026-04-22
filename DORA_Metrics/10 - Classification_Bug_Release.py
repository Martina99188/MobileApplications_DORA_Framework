import pandas as pd

INPUT_FILE = "./extracted_data/change_failure_rate.csv"
OUTPUT_FILE = "./extracted_data/change_failure_rate_classified.csv"

df = pd.read_csv(INPUT_FILE)

def classify_cfr(val):
    if pd.isna(val):
        return None
    if val < 0.1:
        return "Elite"
    elif val < 0.5:
        return "High"
    elif val < 1.0:
        return "Medium"
    else:
        return "Low"

df["cfr_level"] = df["change_failure_rate_percent"].apply(classify_cfr)

df.to_csv(OUTPUT_FILE, index=False)

print(f"[INFO] CFR classification saved in {OUTPUT_FILE}")