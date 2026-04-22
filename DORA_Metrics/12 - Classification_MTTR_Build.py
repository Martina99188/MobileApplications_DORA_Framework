import pandas as pd

INPUT_FILE = "./extracted_data/mttr_builds.csv"
OUTPUT_FILE = "./extracted_data/mttr_builds_classified.csv"

df = pd.read_csv(INPUT_FILE)

def classify_mttr(hours):
    if pd.isna(hours):
        return None
    if hours < 1:
        return "Elite"
    elif hours < 24:
        return "High"
    elif hours <= 72:
        return "Medium"
    else:
        return "Low"

df["mttr_build_level"] = df["mttr_build_hours"].apply(classify_mttr)

df.to_csv(OUTPUT_FILE, index=False)

print(f"[INFO] MTTR classification saved in {OUTPUT_FILE}")