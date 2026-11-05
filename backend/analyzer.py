import pandas as pd

def analyze_data(df):

    print("Column names:", df.columns.tolist())

    print(
        "Duplicate column names:",
        df.columns[df.columns.duplicated()].tolist()
    )


    report = {
        "total_rows": df.shape[0],
        "total_columns": df.shape[1],
        "missing_values": df.isnull().sum().to_dict(),
        "missing_percentage": ((df.isnull().sum() / len(df)) * 100).to_dict(),
        "duplicates_count": int(df.duplicated().sum()),
        "data_types": df.dtypes.astype(str).to_dict()
    }

    cleaned_df = df.drop_duplicates().copy()
    for column in cleaned_df.columns:
        if cleaned_df[column].isnull().sum() > 0:
            if pd.api.types.is_numeric_dtype(cleaned_df[column]):
                cleaned_df[column] = cleaned_df[column].fillna(cleaned_df[column].median())

            else:
                mode = cleaned_df[column].mode()
                if not mode.empty:
                    cleaned_df[column] = cleaned_df[column].fillna(mode[0])

    return report, cleaned_df