
import pandas as pd


def analyze_data(df):

    report = {
        "total_rows": df.shape[0],
        "total_columns": df.shape[1],
        "missing_values": df.isnull().sum().to_dict(),
        "missing_percentage": (
            (df.isnull().sum() / len(df)) * 100
        ).to_dict(),
        "duplicates_count": int(df.duplicated().sum()),
        "data_types": df.dtypes.astype(str).to_dict()
    }

    cleaned_df = clean_data(
        df,
        duplicate_option="Remove",
        numeric_strategy="Median",
        categorical_strategy="Mode"
    )

    return report, cleaned_df


def clean_data(
    df,
    duplicate_option="Remove",
    numeric_strategy="Median",
    categorical_strategy="Mode"
):

    cleaned_df = df.copy()

    # 1. Handle duplicate rows
    if duplicate_option == "Remove":
        cleaned_df = cleaned_df.drop_duplicates()

    # 2. Handle missing values
    for column in cleaned_df.columns:

        if cleaned_df[column].isnull().sum() == 0:
            continue

        # Numerical columns
        if pd.api.types.is_numeric_dtype(cleaned_df[column]):

            if numeric_strategy == "Mean":
                fill_value = cleaned_df[column].mean()

            elif numeric_strategy == "Median":
                fill_value = cleaned_df[column].median()

            elif numeric_strategy == "Zero":
                fill_value = 0

            else:
                continue

            if pd.notna(fill_value):
                cleaned_df[column] = cleaned_df[column].fillna(fill_value)

        # Categorical columns
        else:

            if categorical_strategy == "Mode":
                mode = cleaned_df[column].mode()

                if not mode.empty:
                    cleaned_df[column] = cleaned_df[column].fillna(mode[0])

            elif categorical_strategy == "Unknown":
                cleaned_df[column] = cleaned_df[column].fillna("Unknown")

    return cleaned_df
