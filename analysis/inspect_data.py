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

    print("\n" + "=" * 70)
    print("FILE:", file)
    print("=" * 70)

    # Read only a sample first
    df = pd.read_csv(path, nrows=10000)

    print("\nColumns:")
    print(df.columns.tolist())

    print("\nSample shape:")
    print(df.shape)

    print("\nFirst 5 rows:")
    print(df.head())

    print("\nMissing values:")
    print(df.isnull().sum())

    print("\nDuplicate rows in sample:")
    print(df.duplicated().sum())

    print("\nData types:")
    print(df.dtypes)