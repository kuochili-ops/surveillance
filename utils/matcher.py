import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# 載入自製模組
from utils.crawler import fetch_fda_dsc_alerts, parse_dsc_to_fda_list
from utils.matcher import match_fda_to_tfda
from utils.tfda_loader import load_tfda_data

# 頁面設定
st.set_page_config(page_title="藥品警訊系統", layout="wide")
st.title("藥品警訊系統")

# 載入 TFDA 資料
tfda_list = load_tfda_data()

# 顯示 TFDA 載入狀態
if tfda_list:
    st.success(f"✅ 已載入 TFDA 許可證資料，共 {len(tfda_list)} 筆")
else:
    st.warning("⚠️ 無法載入 TFDA 許可證資料，請確認 data/tfda.json 是否存在且格式正確")

# 抓取 FDA 官網警示
alerts = fetch_fda_dsc_alerts()
fda_list = parse_dsc_to_fda_list(alerts)

# 建立比對結果 DataFrame
df = pd.DataFrame(match_fda_to_tfda(fda_list, tfda_list))

# Sidebar 切換選項
with st.sidebar:
    st.markdown("---")
    date_range_option = st.radio(
        "警示日期範圍",
        ("近三個月", "近一年", "全部警示"),
        index=0
    )

# 根據選項決定篩選範圍
today = datetime.today()
if date_range_option == "近三個月":
    start_date = today - timedelta(days=90)
elif date_range_option == "近一年":
    start_date = today - timedelta(days=365)
else:
    start_date = None  # 全部警示，不篩選

# 篩選資料
if "Alert Date" in df.columns:
    df["Alert Date"] = pd.to_datetime(df["Alert Date"], errors="coerce")
    if start_date:
        df = df[df["Alert Date"] >= start_date]

# 顯示結果
if not df.empty:
    st.dataframe(df, use_container_width=True)
else:
    st.info("目前沒有符合篩選條件的 FDA 藥品警示。")

# Sidebar 註記
with st.sidebar:
    st.caption(f"📅 系統目前顯示 {date_range_option} 的 FDA 藥品警示")
