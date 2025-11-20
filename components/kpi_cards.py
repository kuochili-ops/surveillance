import streamlit as st

def render_kpi(df):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="本期警示數", value=len(df))
    with col2:
        st.metric(label="新增黑框警語數", value=1)  # TODO: 可改成自動計算
    with col3:
        st.metric(label="台灣有配對藥品數", value=(df["TW Match Status"] != "無配對").sum())
    with col4:
        st.metric(label="需人工覆核數", value=(df["Match Confidence"] < 0.7).sum())
    st.markdown("---")
