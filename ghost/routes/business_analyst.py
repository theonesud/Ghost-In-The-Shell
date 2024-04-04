import openai
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


def main():
    st.title("Business Data Query Processor")

    # File uploader for the dataset
    data_file = st.file_uploader(
        "Upload your sales, inventory, or user data (CSV)", type="csv"
    )
    data_frame = pd.DataFrame()
    if data_file is not None:
        data_frame = pd.read_csv(data_file)
        st.write("Data Preview:", data_frame.head())

    # Text input for user's business question
    description = st.text_input(
        "Describe your business question",
        "Example: Calculate the total sales for last month.",
    )

    if st.button("Generate and Execute Query"):
        with st.spinner("Processing..."):
            # Generate Python query
            python_query = generate_python_query(description)
            st.text_area("Generated Python Query", python_query, height=150)

            # Execute the generated query
            if not data_frame.empty:
                result = execute_python_query(python_query, data_frame)
                st.write("Query Result:")
                st.write(result)


if __name__ == "__main__":
    main()
