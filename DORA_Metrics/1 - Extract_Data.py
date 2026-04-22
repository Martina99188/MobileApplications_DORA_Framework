import pandas as pd
from pathlib import Path

Q3_FILE = "./DORA_Metrics/DF_release.csv"
ODS_FILE = "./ManualAnalysis/ReporitoryList + ManualAnalysis.ods"
OUTPUT_DIR = "./extracted_data"
OUTPUT_FILE = "repositories_full.csv"

def main():
    output_path = Path(OUTPUT_DIR)
    output_path.mkdir(parents=True, exist_ok=True)

    q3_df = pd.read_csv(Q3_FILE)
    q3_df = q3_df.dropna(subset=["RepositoryName"])
    q3_df = q3_df.drop_duplicates(subset=["RepositoryName"])

    q3_df["RepositoryName"] = q3_df["RepositoryName"].astype(str).str.strip()

    ods_df = pd.read_excel(ODS_FILE, engine="odf")
    ods_df = ods_df.dropna(subset=["Link Github"])

    ods_df["Link Github"] = ods_df["Link Github"].astype(str).str.strip()

    ods_df["full_name"] = ods_df["Link Github"].str.replace(
        "https://github.com/", "", regex=False
    )

    ods_df["repo_simple"] = ods_df["full_name"].apply(lambda x: x.split("/")[-1])

    repo_map = dict(zip(ods_df["repo_simple"], ods_df["full_name"]))

    full_names = []

    for repo in q3_df["RepositoryName"]:
        if repo in repo_map:
            full_names.append(repo_map[repo])
        else:
            full_names.append("")

    result_df = pd.DataFrame({
        "repository_name": q3_df["RepositoryName"],
        "full_name": full_names
    })

    result_df.to_csv(output_path / OUTPUT_FILE, index=False)

    print("Total number of lines:", len(result_df))
    print("Not found:", result_df["full_name"].eq("").sum())
    print("Saved in:", output_path / OUTPUT_FILE)


if __name__ == "__main__":
    main()
