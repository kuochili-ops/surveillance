import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# 載入自製模組
from utils.crawler import fetch_fda_dsc_alerts, parse_dsc_to_fda_list
from utils.matcher import match_fda_to_tfda
from utils.tfda_loader import load_tfda_data 

st.set_page_config(page_title="藥品警訊", layout="wide")

st.title("藥品警訊系統")

# 載入 TFDA 資料
tfda_list = load_tfda_data()

# 抓取 FDA 官網警示
alerts = fetch_fda_dsc_alerts()
fda_list = parse_dsc_to_fda_list(alerts)

# 建立比對結果 DataFrame
df = pd.DataFrame(match_fda_to_tfda(fda_list, tfda_list))

# 篩選近三個月的警示
if "Alert Date" in df.columns:
    today = datetime.today()
    three_months_ago = today - timedelta(days=90)
    df["Alert Date"] = pd.to_datetime(df["Alert Date"], errors="coerce")
    df = df[df["Alert Date"] >= three_months_ago]

# 顯示結果
if not df.empty:
    st.dataframe(df, use_container_width=True)
else:
    st.info("目前近三個月內沒有符合的 FDA 藥品警示。")

# Sidebar 註記
with st.sidebar:
    st.markdown("---")
    st.caption("📘 **DSC（Drug Safety Communication）** 是 FDA 發布的藥品安全警示，內容包含新發現的副作用、風險族群與使用建議。")
    st.caption("📅 系統僅顯示近三個月內的 FDA 藥品警示")
