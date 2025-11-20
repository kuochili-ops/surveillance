import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# 自製模組
from utils.crawler import fetch_fda_dsc_alerts, parse_dsc_to_fda_list, fetch_fda_dsc_current
from utils.matcher import match_fda_to_tfda
from utils.tfda_loader import load_tfda_data

# 頁面設定
st.set_page_config(page_title="藥品警訊系統", layout="wide")
st.title("藥品警訊系統")

# 載入 TFDA 資料
tfda_list = load_tfda_data()
if tfda_list:
    st.success(f"✅ 已載入 TFDA 許可資訊資料，共 {len(tfda_list)} 筆")
else:
    st.warning("⚠️ 無法載入 TFDA 許可證資料，請確認 data/tfda.json 是否存在且格式正確")

# 抓取 FDA 官網警訊
alerts = fetch_fda_dsc_alerts()
fda_list = parse_dsc_to_fda_list(alerts)

# 建立比對結果 DataFrame
df = pd.DataFrame(match_fda_to_tfda(fda_list, tfda_list))

# Sidebar：切換警示範圍（移除「全部警示」）
with st.sidebar:
    st.markdown("---")
    date_range_option = st.radio(
        "📅 警示日期範圍",
        ("近三個月", "近一年"),
        index=0
    )

# 日期轉換與篩選
if "Alert Date" in df.columns:
    df["Alert Date"] = pd.to_datetime(df["Alert Date"], errors="coerce")
    today = datetime.today()

    if date_range_option == "近三個月":
        start_date = today - timedelta(days=90)
        df = df[df["Alert Date"] >= start_date]
    elif date_range_option == "近一年":
        start_date = today - timedelta(days=365)
        df = df[df["Alert Date"] >= start_date]

# 主頁面：關鍵字搜尋欄位
keyword = st.text_input("🔍 關鍵字搜尋（產品名 / 成分 / 風險摘要）")
if keyword:
    keyword_lower = keyword.lower()
    df = df[df.apply(
        lambda row: keyword_lower in str(row.get("US Product", "")).lower()
        or keyword_lower in str(row.get("Ingredient", "")).lower()
        or keyword_lower in str(row.get("Risk Summary", "")).lower(),
        axis=1
    )]

# 篩選診斷區塊
with st.expander("📊 篩選診斷"):
    st.write("目前筆數：", len(df))
    st.write("最早日期：", df["Alert Date"].min())
    st.write("最晚日期：", df["Alert Date"].max())
    st.write("無效日期筆數（NaT）：", df["Alert Date"].isna().sum())

# 顯示結果
if not df.empty:
    st.dataframe(df, use_container_width=True)
else:
    st.info("目前沒有符合條件的 FDA 藥品警示。")

# 顯示 FDA 官網目前 DSC 警訊（簡易表格）
with st.expander("📢 FDA 官網目前 DSC 藥品警訊"):
    current_alerts = fetch_fda_dsc_current()
    st.write(f"共 {len(current_alerts)} 筆")
    st.table(current_alerts)

# Sidebar 註記
with st.sidebar:
    st.caption("📘 DSC（Drug Safety Communication）是 FDA 發布的藥品安全警示，內容包含新發現的副作用、風險族群與使用建議。")
    st.caption(f"📅 系統目前顯示「{date_range_option}」內的 FDA 藥品警示")
