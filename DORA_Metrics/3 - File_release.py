import pandas as pd

repos_full = pd.read_csv("./extracted_data/repositories_full.csv")
releases_df = pd.read_csv("./extracted_data/releases.csv")

repos_full["full_name"] = repos_full["full_name"].fillna("").astype(str).str.strip()

repos_full["repo_only"] = repos_full["full_name"].apply(
    lambda x: x.split("/")[-1] if "/" in x else ""
)

releases_mapped = releases_df.merge(
    repos_full[["repo_only", "full_name"]],
    left_on="repository",
    right_on="repo_only",
    how="left"
)

releases_mapped["repository"] = releases_mapped["full_name"]

releases_mapped = releases_mapped.drop(columns=["repo_only", "full_name"])

releases_mapped.to_csv("./extracted_data/releases_mapped.csv", index=False)
print("Mapping completed. File saved to releases_mapped.csv")
