import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from difflib import SequenceMatcher
import os

# -------------------------
# 標準化處理
# -------------------------
def normalize_text(text):
    if not text:
        return ""
    return (
        str(text).lower()
        .replace(" ", "")
        .replace("劑", "")
        .replace("注射液劑", "注射液")
        .replace("毫克", "mg")
        .replace("毫升", "ml")
    )

# -------------------------
# 配對模組
# -------------------------
def fuzzy_match(a, b):
    return SequenceMatcher(None, a, b).ratio()

def compute_match_score(fda, tfda):
    fda_ing = normalize_text(fda.get("ingredient", ""))
    tfda_ing = normalize_text(tfda.get("ingredient", ""))
    fda_form = normalize_text(fda.get("form", ""))
    tfda_form = normalize_text(tfda.get("form", ""))
    fda_prod = normalize_text(fda.get("us_product", ""))
    tfda_prod = normalize_text(tfda.get("tw_product", ""))

    score = 0.0
    if fda_ing and tfda_ing:
        if fda_ing == tfda_ing:
            score += 0.6
        elif fda_ing.split()[0] == tfda_ing.split()[0]:
            score += 0.5

    if fda_form and tfda_form:
        if fda_form == tfda_form:
            score += 0.3
        elif fda_form.split()[0] == tfda_form.split()[0]:
            score += 0.2

    if fda_prod and tfda_prod:
        sim = fuzzy_match(fda_prod, tfda_prod)
        if sim >= 0.85:
            score += 0.1
        elif sim >= 0.7:
            score += 0.05

    return round(score, 2)

def match_fda_to_tfda(fda_list, tfda_list):
    results = []
    for fda in fda_list:
        best_match = None
        best_score = 0.0
        for tfda in tfda_list:
            score = compute_match_score(fda, tfda)
            if score > best_score:
                best_score = score
                best_match = tfda
        if best_match and best_score >= 0.5:
            results.append({
                "Alert Date": fda["alert_date"],
                "Source": fda["source"],
                "US Product": fda["us_product"],
                "Ingredient": fda["ingredient"],
                "Risk Summary": fda["risk_summary"],
                "Action Summary": fda["action_summary"],
                "TW Match Status": "同主成分" if best_score >= 0.85 else "中信度配對",
                "TW Product": best_match["tw_product"],
                "License ID": best_match["license_id"],
                "Strength/Form": best_match["form"],
                "Match Confidence": best_score,
                "FDA Excerpt": fda["fda_excerpt"]
            })
        else:
            results.append({
                "Alert Date": fda["alert_date"],
                "Source": fda["source"],
                "US Product": fda["us_product"],
                "Ingredient": fda["ingredient"],
                "Risk Summary": fda["risk_summary"],
                "Action Summary": fda["action_summary"],
                "TW Match Status": "無配對",
                "TW Product": "",
                "License ID": "",
                "Strength/Form": "",
                "Match Confidence": 0.0,
                "FDA Excerpt": fda["fda_excerpt"]
            })
    return results

# -------------------------
# FDA 官網爬蟲 + 新警示監視
# -------------------------
def fetch_fda_dsc_alerts():
    url = "https://www.fda.gov/drugs/drug-safety-and-availability/drug-safety-communications"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    alerts = []
    for item in soup.select(".view-content .views-row"):
        title_tag = item.select_one("h3 a")
        date_tag = item.select_one(".date-display-single")
        if title_tag and date_tag:
            alerts.append({
                "title": title_tag.text.strip(),
                "link": "https://www.fda.gov" + title_tag["href"],
                "date": date_tag.text.strip()
            })
    return alerts

def parse_dsc_to_fda_list(alerts):
    parsed = []
    for alert in alerts:
        parsed.append({
            "alert_date": pd.to_datetime(alert["date"], errors="coerce"),
            "source": "DSC",
            "us_product": alert["title"].split(":")[0].strip(),
            "ingredient": "",
            "form": "",
            "risk_summary": alert["title"],
            "action_summary": "請參考原文",
            "fda_excerpt": f"詳情請見：{alert['link']}"
        })
    return parsed

def load_last_seen():
    if os.path.exists("last_seen_alerts.json"):
        try:
            return pd.read_json("last_seen_alerts.json")["title"].tolist()
        except:
            return []
    return []

def save_last_seen(alerts):
    titles = [a["title"] for a in alerts]
    pd.DataFrame({"title": titles}).to_json("last_seen_alerts.json")

def get_new_alerts():
    latest = fetch_fda_dsc_alerts()
    seen = load_last_seen()
    new_alerts = [a for a in latest if a["title"] not in seen]
    save_last_seen(latest)
    return new_alerts

# -------------------------
# 預設 FDA 藥品清單
# -------------------------
fda_list = [
    {
        "alert_date": "2025-11-01",
        "source": "DSC",
        "us_product": "Leqembi",
        "ingredient": "lecanemab",
        "form": "100 mg/mL 注射液",
        "risk_summary": "阿茲海默症 ARIA：APOE ε4 攜帶者風險增加",
        "action_summary": "建議基因檢測",
        "fda_excerpt": "FDA recommends MRI monitoring to reduce ARIA risk, especially in APOE ε4 carriers."
    },
    {
        "alert_date": "2025-10-15",
        "source": "DSC",
        "us_product": "Prolia",
        "ingredient": "denosumab",
        "form": "60 mg/1 mL 注射液",
        "risk_summary": "嚴重低血鈣：洗腎病人風險增加",
        "action_summary": "建議監測血鈣",
        "fda_excerpt": "Risk of severe hypocalcemia in dialysis patients receiving denosumab."
    }
]

# -------------------------
# Streamlit 主畫面
# -------------------------
st.set_page_config(page_title="藥品安全警示比對平台", layout="wide")
st.title("藥品安全警示比對平台")

# 直接讀取同目錄下的 37_2b.csv
try:
    df_tfda = pd.read_csv("37_2b.csv")
    required_cols = ["tw_product", "ingredient", "form", "license_id"]
    if not all(col in df_tfda.columns for col in required_cols):
        st.error("37_2b.csv 欄位缺漏，請確認包含：tw_product, ingredient, form, license_id")
        tfda_list = []
    else:
        tfda_list = df_tfda[required_cols].to_dict(orient="records")
except Exception as e:
    st.error(f"讀取 37_2b.csv 失敗：{e}")
    tfda_list = []

df = pd.DataFrame(match_fda_to_tfda(fda_list, tfda_list))

# 防呆：空資料
if df.empty:
    st.warning("⚠️ 沒有配對結果，請確認 TFDA 資料與 FDA 清單格式。")
    st.stop()

# 防呆：欄位缺失
if "Alert Date" in df.columns:
    df["Alert Date"] = pd.to_datetime(df["Alert Date"])
else:
    st.warning("⚠️ 欄位 'Alert Date' 不存在，無法轉換日期格式。")
    st.stop()

# KPI 卡片
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="本期警示數", value=len(df))
with col2:
    st.metric(label="新增黑框警語數", value=1)
with col3:
    st.metric(label="台灣有配對藥品數", value=(df["TW Match Status"] != "無配對").sum())
with col4:
    st.metric(label="需人工覆核數", value=(df["Match Confidence"] < 0.7).sum())

st.markdown("---")
# 篩選器
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

# 主表格顯示
st.markdown("### 📋 配對結果一覽")
st.dataframe(df_filtered, use_container_width=True)

# 詳情展開
with st.expander("📦 展開每筆警示詳情"):
    for _, row in df_filtered.iterrows():
        st.markdown(f"**🧪 {row['US Product']}**（{row['Ingredient']}）")
        st.markdown(f"- 警示日期：{row['Alert Date'].date()}｜來源：{row['Source']}")
        st.markdown(f"- 台灣配對：{row['TW Match Status']} → `{row['TW Product']}`")
        st.markdown(f"- 摘要：{row['Risk Summary']}")
        st.markdown(f"- 建議：{row['Action Summary']}")
        st.markdown(f"- 詳情：{row['FDA Excerpt']}")
        st.markdown("---")

# FDA 官網爬蟲按鈕
st.markdown("### 🔁 一鍵抓取並比對 FDA 官網警示")
if st.button("立即更新"):
    latest_alerts = fetch_fda_dsc_alerts()
    fda_list_from_web = parse_dsc_to_fda_list(latest_alerts)
    df = pd.DataFrame(match_fda_to_tfda(fda_list_from_web, tfda_list))
    df["Alert Date"] = pd.to_datetime(df["Alert Date"])
    st.dataframe(df, use_container_width=True)

# 網頁監視：檢查是否有新警示
st.markdown("### 🔍 檢查 FDA 官網是否有新警示")
if st.button("檢查新警示並比對"):
    new_alerts = get_new_alerts()
    if new_alerts:
        st.success(f"發現 {len(new_alerts)} 筆新警示！")
        fda_list_new = parse_dsc_to_fda_list(new_alerts)
        df_new = pd.DataFrame(match_fda_to_tfda(fda_list_new, tfda_list))
        df_new["Alert Date"] = pd.to_datetime(df_new["Alert Date"])
        st.dataframe(df_new, use_container_width=True)
    else:
        st.info("目前沒有新警示。")

