import pandas as pd

def analyze_data(df):

    total_rows = df.shape[0]
    total_columns = df.shape[1]

    missing_values = df.isnull().sum()
    missing_percentage = (missing_values/total_rows)*100

    duplicates_count = df.duplicated().sum()
    cleaned_df = df.drop_duplicates()

    #Display the Report
    print("Total Rows: ", total_rows)
    print("Missing Values: ")
    print(missing_values)

    print("Missing Value Percentage: ")
    print(missing_percentage)

    print("Duplicate Count: ", duplicates_count)

    print("Replace Nan with Mean: ")
    cleaned_df = cleaned_df.fillna(df['Age'].mean())
    cleaned_df = cleaned_df.fillna(df['Salary'].median())
    print(cleaned_df)

    return cleaned_df



data = {
    "Name": ["Asha", "Rahul", "Priya", "Asha", "John", "Rahul"],
    "Age": [22, 25, None, 22, 24, 25],
    "Salary": [25000, 35000, 28000, 25000, None, 35000]
}

df = pd.DataFrame(data)
cleaned_data = analyze_data(df)