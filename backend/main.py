import pandas as pd
from analyzer import analyze_data

data = {
    "Name": ["Asha", "Rahul", "Priya", "Asha", "John", "Rahul"],
    "Age": [22, 25, None, 22, 24, 25],
    "Salary": [25000, 35000, 28000, 25000, None, 35000]
}

df = pd.DataFrame(data)

report, cleaned_df = analyze_data(df)

print("\nData Quality Report")
print("-" * 30)

print(f"Total Rows      : {report['total_rows']}")
print(f"Total Columns   : {report['total_columns']}")
print(f"Duplicate Count : {report['duplicates_count']}")

print("\nMissing Values:")
for col, count in report['missing_values'].items():
    print(f"  {col}: {count}")

print("\nMissing Percentage:")
for col, per in report['missing_percentage'].items():
    print(f"  {col}: {per:.2f}%")

print(f"\n Data Types: {report['data_types']}")