import streamlit as st
from utils.crawler import fetch_fda_dsc_alerts

st.title("FDA 官網爬蟲診斷工具")

alerts = fetch_fda_dsc_alerts()
st.write(f"📦 共抓到 {len(alerts)} 筆 FDA DSC 警訊")

if alerts:
    st.table(alerts[:10])
else:
    st.error("❌ 沒有抓到任何警訊，可能啟用了 fallback 或爬蟲失敗")
