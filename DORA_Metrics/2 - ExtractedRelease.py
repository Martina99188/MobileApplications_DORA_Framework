import pandas as pd

INPUT_FILE = "./DORA_Metrics/CLT_days.csv"
OUTPUT_FILE = "./extracted_data/releases.csv"

df = pd.read_csv(INPUT_FILE, parse_dates=[
    "ReleaseBeforeDatetime",
    "ReleaseAfterDatetime"
])

releases_after = df[[
    "RepositoryName",
    "FirstReleaseAfterCommit",
    "ReleaseAfterDatetime"
]].dropna()

releases_after.columns = ["repository", "release_tag", "release_date"]

releases_after = releases_after.drop_duplicates()

releases_after.to_csv(OUTPUT_FILE, index=False)
