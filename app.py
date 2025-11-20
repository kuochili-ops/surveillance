import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import re

# 成分抽取工具
def extract_product_and_ingredient(title):
    match = re.search(r"([A-Za-z0-9\-]+)\s*\(([^)]+)\)", title)
    if match:
        return match.group(1), match.group(2)
    return "", ""

# 匯入自製模組
from utils.crawler import fetch_fda_dsc_alerts
from utils.selenium_crawler import fetch_fda_dsc_alerts_selenium
from utils.matcher import match_fda_to_tfda
from utils.tfda_loader import load_tfda_data

# FDA 警訊解析
def parse_dsc_to_fda_list(alerts):
    results = []
    for alert in alerts:
        product, ingredient = extract_product_and_ingredient(alert.get("title", ""))
        results.append({
            "alert_date": alert.get("alert_date", None),
            "source": alert.get("source", "FDA"),
            "us_product": product,
            "ingredient": ingredient,
            "risk_summary": alert.get("title", ""),
            "action_summary": "",
            "fda_excerpt": alert.get("title", "")
        })
    return results

# 頁面設定
st.set_page_config(page_title="藥品警訊系統", layout="wide")
st.title("藥品警訊系統")

# Sidebar：爬蟲模式切換
with st.sidebar:
    st.markdown("### ⚙️ 爬蟲模式")
    crawler_mode = st.radio("選擇資料來源", ("Requests", "Selenium"), index=0)

# 載入 TFDA 資料
tfda_list = load_tfda_data()
if tfda_list:
    st.success(f"✅ 已載入 TFDA 許可資訊資料，共 {len(tfda_list)} 筆")
else:
    st.warning("⚠️ 無法載入 TFDA 許可證資料，請確認 data/tfda.json 是否存在且格式正確")

# 抓取 FDA 官網警訊
if crawler_mode == "Requests":
    alerts = fetch_fda_dsc_alerts()
else:
    alerts = fetch_fda_dsc_alerts_selenium()

fda_list = parse_dsc_to_fda_list(alerts)

if not fda_list:
    st.error("⚠️ 無法取得 FDA 藥品警訊資料，請檢查 crawler 或 selenium_crawler")
    st.stop()

# 建立比對結果 DataFrame
df_raw = pd.DataFrame(match_fda_to_tfda(fda_list, tfda_list))
df_raw["Alert Date"] = pd.to_datetime(df_raw["Alert Date"], errors="coerce")
df = df_raw.copy()

# Sidebar：切換警示範圍
with st.sidebar:
    st.markdown("---")
    date_range_option = st.radio("📅 警示日期範圍", ("近三個月", "近一年"), index=0)

# 日期篩選
today = datetime.today()
if date_range_option == "近三個月":
    start_date = today - timedelta(days=90)
elif date_range_option == "近一年":
    start_date = today - timedelta(days=365)

df = df[df["Alert Date"].notna() & (df["Alert Date"] >= start_date)]

# 主頁面：關鍵字搜尋
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
    st.write("目前筆數（未篩選）：", len(df_raw))
    st.write("目前筆數（已篩選）：", len(df))
    st.write("最早日期（未篩選）：", df_raw["Alert Date"].min())
    st.write("最晚日期（未篩選）：", df_raw["Alert Date"].max())
    st.write("最早日期（已篩選）：", df["Alert Date"].min() if not df.empty else "無資料")
    st.write("最晚日期（已篩選）：", df["Alert Date"].max() if not df.empty else "無資料")
    st.write("無效日期筆數（NaT）：", df_raw["Alert Date"].isna().sum())
    st.caption(f"📅 篩選起始日：{start_date.date()}（依據「{date_range_option}」選項）")

# 顯示結果
if not df.empty:
    st.dataframe(df, use_container_width=True)
else:
    st.info("目前沒有符合條件的 FDA 藥品警示。")

# 🔍 FDA 成分比對診斷
with st.expander("🧪 FDA 成分比對診斷"):
    unmatched = []
    for fda in fda_list:
        fda_ing = fda.get("ingredient", "").lower()
        if fda_ing and not any(tfda.get("ingredient", "").lower() == fda_ing for tfda in tfda_list):
            unmatched.append(fda_ing)
    if unmatched:
        st.warning(f"共有 {len(unmatched)} 筆 FDA 成分無法比對 TFDA：")
        st.write(sorted(set(unmatched)))
    else:
        st.success("✅ 所有 FDA 成分皆成功比對 TFDA")

# Sidebar 註記
with st.sidebar:
    st.caption("📘 DSC（Drug Safety Communication）是 FDA 發布的藥品安全警示，內容包含新發現的副作用、風險族群與使用建議。")
    st.caption(f"📅 系統
