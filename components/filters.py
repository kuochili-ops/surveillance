import streamlit as st
import pandas as pd

def apply_filters(df):
    st.sidebar.header("篩選器")
    min_date = df["Alert Date"].min().date()
    max_date = df["Alert Date"].max().date()
    date_range = st.sidebar.date_input("警示日期範圍", value=(min_date, max_date), min_value=min_date, max_value=max_date)
    source_options = df["Source"].unique().tolist()
    selected_sources = st.sidebar.multiselect("來源類型", options=source_options, default=source_options)
    keyword = st.sidebar.text_input("關鍵字搜尋（品名 / 成分 / 摘要）", value="")

    start_date, end_date = date_range if isinstance(date_range, tuple) else (min_date, max_date)
    df_filtered = df[
        (df["Alert Date"] >= pd.to_datetime(start_date)) &
        (df["Alert Date"] <= pd.to_datetime(end_date)) &
        (df["Source"].isin(selected_sources))
    ]
    if keyword.strip():
        kw = keyword.strip().lower()
        df_filtered = df_filtered[df_filtered.apply(lambda row: kw in str(row).lower(), axis=1)]

    return df_filtered
