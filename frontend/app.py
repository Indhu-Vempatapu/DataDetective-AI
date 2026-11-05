import streamlit as st
import pandas as pd
import sys
from pathlib import Path
from io import BytesIO
import altair as alt
#Backend Connection
backend_path = Path(__file__).resolve().parents[1]/ "backend"
sys.path.append(str(backend_path))

from analyzer import analyze_data

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
            df = pd.read_excel(uploaded_file, header=1)

        st.subheader("Dataset Preview")
        st.dataframe(df, width="stretch")

        #Connect Analyzer
        report, cleaned_df = analyze_data(df)
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

        st.subheader("Cleaned Dataset")
        st.dataframe(cleaned_df, width="stretch")

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