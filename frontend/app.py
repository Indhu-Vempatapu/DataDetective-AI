import streamlit as st
import pandas as pd
import sys
from pathlib import Path
from io import BytesIO
import altair as alt
#Backend Connection
backend_path = Path(__file__).resolve().parents[1]/ "backend"
sys.path.append(str(backend_path))

from analyzer import analyze_data, clean_data

#Page Configuration
st.set_page_config(
    page_title = "DataDetective AI",
    page_icon = "🔍",
    layout = "wide"
)

#Application Title and Description

st.title("DataDetective AI")
st.write("Your AI-powered Data Quality Analyzer")

st.success("Welcome! Upload your dataset to get started.")

#File Upload
uploaded_file = st.file_uploader("Upload your data file", type = ["csv", "xlsx"])
if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file, header=0)

        st.subheader("Dataset Preview")
        st.dataframe(df, width="stretch")

        #Connect Analyzer
        report, _ = analyze_data(df)
        st.subheader("Data Quality Report")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Rows", report["total_rows"])
        col2.metric("Total Columns", report["total_columns"])
        col3.metric("Duplicates Count", report["duplicates_count"])

        st.subheader("Missing Values")

        # Get missing value information
        missing_counts = report["missing_values"]
        missing_percentages = report["missing_percentage"]

        # Convert both into Pandas Series
        missing_counts = pd.Series(missing_counts)
        missing_percentages = pd.Series(missing_percentages)

        # Create a DataFrame
        missing_df = pd.DataFrame({
            "Missing Count": missing_counts,
            "Missing Percentage": missing_percentages
        })

        # Convert column names into a separate column
        missing_df.index.name = "Column"
        missing_df = missing_df.reset_index()

        # Format percentages
        missing_df["Missing Percentage"] = missing_df[
            "Missing Percentage"
        ].map(lambda value: f"{value:.2f}%")

        # Display table
        st.dataframe(missing_df, width="stretch")

        st.subheader("Data Types")
        st.json(report["data_types"])
        
        # Interactive Data Cleaning
        st.subheader("Interactive Data Cleaning")

        st.write("Choose how you want to clean your dataset.")

        # 1. Duplicate Handling
        duplicate_option = st.selectbox(
            "How should duplicate rows be handled?",
            ["Remove", "Keep"]
        )

        # 2. Numerical Missing Values
        numeric_strategy = st.selectbox(
            "How should missing numerical values be handled?",
            ["Keep", "Mean", "Median", "Zero"]
        )

        # 3. Categorical Missing Values
        categorical_strategy = st.selectbox(
            "How should missing categorical values be handled?",
            ["Keep", "Mode", "Unknown"]
        )

        # Apply selected cleaning options
        cleaned_df = clean_data(
            df,
            duplicate_option=duplicate_option,
            numeric_strategy=numeric_strategy,
            categorical_strategy=categorical_strategy
        )

        st.success("Cleaning applied successfully!")

        # Display cleaned dataset
        st.subheader("Cleaned Dataset")
        st.dataframe(cleaned_df, width="stretch")

        # Cleaning Impact Report
        st.subheader("Data Cleaning Impact Report")

        original_rows = len(df)
        cleaned_rows = len(cleaned_df)

        duplicates_removed = original_rows - len(df.drop_duplicates()) if duplicate_option == "Remove" else 0

        original_missing = int(df.isnull().sum().sum())
        remaining_missing = int(cleaned_df.isnull().sum().sum())

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Original Rows", original_rows)
        col2.metric("Cleaned Rows", cleaned_rows)
        col3.metric("Duplicates Removed", duplicates_removed)
        col4.metric("Missing Values Remaining", remaining_missing)

        st.write(f"Original missing values: {original_missing}")
        st.write(f"Missing values remaining: {remaining_missing}")

        
        # Automated Dataset Insights
        st.subheader("Automated Dataset Insights")

        insights = []

        
        # Identify column types for automated insights

        numeric_columns = []
        categorical_columns = []
        date_columns = []

        for column in cleaned_df.columns:

            # Identify date columns using their column names
            if "date" in str(column).lower():
                date_columns.append(column)
                continue

            # Check whether values can be interpreted as numbers
            converted = pd.to_numeric(
                cleaned_df[column],
                errors="coerce"
            )

            valid_values = cleaned_df[column].notna().sum()

            if valid_values > 0 and converted.notna().sum() == valid_values:
                numeric_columns.append(column)

            else:
                categorical_columns.append(column)


        # 1. Numerical Insights
        if numeric_columns:

            st.write("### Numerical Analysis")

            for column in numeric_columns:

                # Skip identifier columns
                if "id" in str(column).lower():
                    continue

                average = cleaned_df[column].mean()

                if pd.notna(average):
                    st.info(
                        f"Average {column}: {average:.2f}"
                    )

        # 2. Missing Value Insights
        st.write("### Data Quality Insights")

        missing_counts = df.isnull().sum()

        if missing_counts.sum() > 0:

            highest_missing_column = missing_counts.idxmax()

            st.warning(
                f"'{highest_missing_column}' has the highest "
                f"number of missing values: "
                f"{missing_counts.max()}."
            )

        else:
            st.success("Your original dataset has no missing values.")

        
        # Categorical Insights
        st.write("### Categorical Analysis")

        if categorical_columns:

            for column in categorical_columns:

                value_counts = cleaned_df[column].value_counts()

                if value_counts.empty:
                    continue

                highest_count = value_counts.max()

                # Only report meaningful repeated categories
                if highest_count == 1:
                    st.info(
                        f"All values in {column} are unique. "
                        "No repeated category found."
                    )
                    continue

                most_common = value_counts[
                    value_counts == highest_count
                ].index.tolist()

                if len(most_common) == 1:

                    st.info(
                        f"Most frequent value in {column}: "
                        f"{most_common[0]} ({highest_count} records)."
                    )

                else:

                    st.info(
                        f"Multiple values are tied for the highest "
                        f"frequency in {column}: "
                        f"{', '.join(map(str, most_common))} "
                        f"({highest_count} records each)."  
                    )

        else:
            st.write("No categorical columns available.")


        if not numeric_columns and not categorical_columns:
            st.info("No numerical or categorical columns available.")

        
        # Date Validation
        st.subheader("Date Validation")

        if date_columns:

            for column in date_columns:

                # Convert values into datetime format
                parsed_dates = pd.to_datetime(
                    cleaned_df[column],
                    errors="coerce",
                    format="mixed",
                    dayfirst=True
                )

                # Count missing and invalid dates
                missing_dates = cleaned_df[column].isna().sum()

                invalid_dates = (
                    cleaned_df[column].notna() &
                    parsed_dates.isna()
                ).sum()

                valid_dates = parsed_dates.dropna()

                st.write(f"### {column}")

                col1, col2, col3 = st.columns(3)

                col1.metric("Valid Dates", len(valid_dates))
                col2.metric("Invalid Dates", int(invalid_dates))
                col3.metric("Missing Dates", int(missing_dates))

                if not valid_dates.empty:

                    st.write(
                        f"Earliest Date: {valid_dates.min().date()}"
                    )

                    st.write(
                        f"Latest Date: {valid_dates.max().date()}"
                    )

                if invalid_dates > 0:
                    st.warning(
                        f"{invalid_dates} invalid date values found in {column}."
                    )

        else:
            st.info("No date columns detected.")



        #Downloading Cleaned Dataset
        st.subheader("Download Dataset")
        col1, col2 = st.columns(2)
        csv_data = cleaned_df.to_csv(index=False, header=True).encode("utf-8")
        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine = "openpyxl") as writer:
            cleaned_df.to_excel(writer, index=False, header=True, sheet_name = "Cleaned Data")

        col1.download_button(label = "Download CSV", data = csv_data, file_name = "Cleaned_dataset.csv", mime="text/csv")
        col2.download_button(label = "Download Excel", data = excel_buffer.getvalue(), file_name = "cleaned_dataset.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        st.subheader("Data Visualization")

        numeric_columns = cleaned_df.select_dtypes(include="number").columns.tolist()
        categorical_columns = cleaned_df.select_dtypes(include=["object","category", "string"]).columns.tolist()

        st.write("Numerical Columns:", numeric_columns)
        st.write("Categorical Columns:", categorical_columns)

        if categorical_columns:

            selected_category = st.selectbox(
                "Select a categorical column for visualization",
                categorical_columns
            )

            # Count the occurrences of each category
            category_counts = cleaned_df[selected_category].value_counts()

            # Convert the counts into a DataFrame
            category_df = category_counts.reset_index()

            category_df.columns = [selected_category, "Count"]

            # Create the chart
            category_chart = alt.Chart(category_df).mark_bar().encode(
                x=alt.X(
                    selected_category,
                    axis=alt.Axis(labelAngle=0)
                ),
                y=alt.Y(
                    "Count:Q",
                    title="Count of Records"
                ),
                tooltip=[selected_category, "Count"]
            )

            st.subheader(f"Distribution of {selected_category}")

            st.altair_chart(category_chart, width="stretch")

        else:
            st.info("No categorical columns available for visualization.")

        if categorical_columns and numeric_columns:
            st.subheader("Compare Numerical Values")
            col1, col2 = st.columns(2)
            with col1:
                selected_group = st.selectbox("Select a categorical column", categorical_columns, key="group_column")
            with col2:
                selected_value = st.selectbox("Select a numerical column", numeric_columns)

            average_data = cleaned_df.groupby(selected_group)[selected_value].mean()
            average_df = average_data.reset_index()

            average_df.columns = [selected_group, "Average"]

            # Create vertical bar chart with horizontal labels
            average_chart = alt.Chart(average_df).mark_bar().encode(x=alt.X(selected_group,
                    axis=alt.Axis(labelAngle=0, labelOverlap=False)
                ),
                y=alt.Y(
                    "Average:Q",
                    title=f"Average {selected_value}"
                ),
                tooltip=[selected_group, "Average"]
            )

            st.subheader(f"Average {selected_value} by {selected_group}")

            st.altair_chart(average_chart, width="stretch")
        else:
            st.info("You need both categorical and numerical columns for this chart.")

        st.subheader("Outlier Detection")

        if numeric_columns:

            outlier_results = []

            for column in numeric_columns:

                Q1 = cleaned_df[column].quantile(0.25)
                Q3 = cleaned_df[column].quantile(0.75)

                IQR = Q3 - Q1

                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR

                outliers = cleaned_df[
                    (cleaned_df[column] < lower_bound) |
                    (cleaned_df[column] > upper_bound)
                ]

                outlier_results.append({
                    "Column": column,
                    "Lower Bound": lower_bound,
                    "Upper Bound": upper_bound,
                    "Outlier Count": len(outliers)
                })

                outlier_df = pd.DataFrame(outlier_results)

            st.write("Outlier Summary")

            st.dataframe(outlier_df, width="stretch")

        else:
            st.info("No numerical columns available for outlier detection.")

    except Exception as e:
        st.error(f"Error processing dataset: {e}")
        st.exception(e)