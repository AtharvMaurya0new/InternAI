import pandas as pd
import os

DATA_FOLDER = "data"

files = [
    "internship.csv",
    "job_data_merged_1.csv",
    "huge_job_recommendation_dataset.csv"
]

for file in files:
    path = os.path.join(DATA_FOLDER, file)

    df = pd.read_csv(path)

    print(file)
    print("Rows:", len(df))
    print("Columns:", len(df.columns))
    print("-" * 40)