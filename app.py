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

# FDA 警訊解析
def parse_dsc_to_fda_list(alerts):
    results = []
    for alert in alerts:
        product, ingredient = extract_product_and_ingredient(alert.get("title", ""))
        results.append({
            "alert_date": alert.get("alert_date", ""),
            "source": alert.get("source", "FDA"),
            "us_product": product,
            "ingredient": ingredient,
            "risk_summary": alert.get("title", ""),
            "action_summary": "",
            "fda_excerpt": alert.get("title", "")
        })
    return results

# 自製模組
from utils.crawler import fetch_fda_dsc_alerts, fetch_fda_dsc_current
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

if not fda_list:
    st.error("⚠️ 無法取得 FDA 藥品警訊資料，請檢查 crawler.py 或網路連線")
    st.stop()

# 建立比對結果 DataFrame（保證欄位完整）
df_raw = pd.DataFrame(match_fda_to_tfda(fda_list, tfda_list))
df = df_raw.copy()


# Sidebar：切換警示範圍
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
    if "Alert Date" in df_raw.columns:
        df_raw["Alert Date"] = pd.to_datetime(df_raw["Alert Date"], errors="coerce")
        st.write("目前筆數（未篩選）：", len(df_raw))
        st.write("最早日期：", df_raw["Alert Date"].min())
        st.write("最晚日期：", df_raw["Alert Date"].max())
        st.write("無效日期筆數（NaT）：", df_raw["Alert Date"].isna().sum())
    else:
        st.write("⚠️ DataFrame 中沒有 'Alert Date' 欄位，現有欄位：", df_raw.columns.tolist())

# 顯示結果
if not df.empty:
    st.dataframe(df, use_container_width=True)
else:
    st.info("目前沒有符合條件的 FDA 藥品警示。")

# 🔍 FDA 成分比對診斷區塊
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

# 顯示 FDA 官網目前 DSC 警訊（簡易表格）
with st.expander("📢 FDA 官網目前 DSC 藥品警訊"):
    current_alerts = fetch_fda_dsc_current()
    st.write("current_alerts 原始資料：", current_alerts)
    st.write(f"共 {len(current_alerts)} 筆")
    if current_alerts:
        st.table(current_alerts)
    else:
        st.error("⚠️ FDA 官網 DSC 警訊目前無法載入或解析")

# Sidebar 註記
with st.sidebar:
    st.caption("📘 DSC（Drug Safety Communication）是 FDA 發布的藥品安全警示，內容包含新發現的副作用、風險族群與使用建議。")
    st.caption(f"📅 系統目前顯示「{date_range_option}」內的 FDA 藥品警示")
