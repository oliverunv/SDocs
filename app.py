import streamlit as st
import pandas as pd
import re
from io import BytesIO

st.set_page_config(layout="wide")

# Load data (your cleaned paragraph-level CSV)
@st.cache_data
def load_data():
    return pd.read_excel("2024_S-Docs_1-100.xlsx", engine="openpyxl")

df = load_data()

st.title("🔍 SDocs Keyword Search")
st.write("Enter one or more keywords or phrases (comma-separated):")

# Keyword input
keywords_input = st.text_input("Keywords", placeholder="e.g., use of force, sanctions, self-defence")

# Process when user submits input
if keywords_input:
    keywords = [k.strip().lower() for k in keywords_input.split(",") if k.strip()]

    def contains_any_keyword(text):
        text_lower = text.lower()
        return any(k in text_lower for k in keywords)

    # Filter paragraphs
    filtered_df = df[df['paragraph'].apply(contains_any_keyword)].copy()

    # Add dummy columns for each keyword
    for kw in keywords:
        filtered_df[kw] = filtered_df['paragraph'].str.lower().apply(lambda x: int(kw in x))

    st.success(f"✅ Found {len(filtered_df)} matching paragraphs.")
    st.dataframe(filtered_df[['symbol', 'title', 'paragraph', 'page_number'] + keywords])

    # Download button
    def convert_df_to_excel(df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Results')
        output.seek(0)
        return output

    excel_file = convert_df_to_excel(filtered_df)
    st.download_button(
        label="📥 Download Results as Excel",
        data=excel_file,
        file_name="filtered_letters.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

