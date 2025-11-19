import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from difflib import SequenceMatcher

def fuzzy_match(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def compute_match_score(fda, tfda):
    score = 0.0
    fda_ing = str(fda.get("ingredient", "")).strip()
    tfda_ing = str(tfda.get("ingredient", "")).strip()
    fda_form = str(fda.get("form", "")).strip()
    tfda_form = str(tfda.get("form", "")).strip()

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

    fda_prod = str(fda.get("us_product", "")).strip()
    tfda_prod = str(tfda.get("tw_product", "")).strip()
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
# TFDA 許可證匯入模組
# -------------------------
def load_tfda_file(file):
    try:
        if file.name.endswith(".csv"):
            df_tfda = pd.read_csv(file)
        else:
            df_tfda = pd.read_excel(file)
        required_cols = ["tw_product", "ingredient", "form", "license_id"]
        if not all(col in df_tfda.columns for col in required_cols):
            st.error("欄位缺漏，請確認包含：tw_product, ingredient, form, license_id")
            return []
        return df_tfda[required_cols].to_dict(orient="records")
    except Exception as e:
        st.error(f"讀取失敗：{e}")
        return []

# -------------------------
# FDA 官網爬蟲模組
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

# -------------------------
# FDA 警示轉換成 fda_list 結構
# -------------------------
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

# -------------------------
# Streamlit 主畫面
# -------------------------
st.set_page_config(page_title="藥品安全警示比對平台", layout="wide")
st.title("藥品安全警示比對平台")

# TFDA 許可證匯入
uploaded_file = st.sidebar.file_uploader("上傳 TFDA 許可證清單（CSV 或 Excel）", type=["csv", "xlsx"])
if uploaded_file:
    tfda_list = load_tfda_file(uploaded_file)
else:
    tfda_list = [
        {"tw_product": "樂意保", "ingredient": "lecanemab", "form": "100 mg/mL 注射液", "license_id": "MOHW-BI-001273"},
        {"tw_product": "骨松益", "ingredient": "denosumab", "form": "60 mg/1 mL 注射液", "license_id": "衛部藥製字第XXXX號"}
    ]

# 預設比對結果
df = pd.DataFrame(match_fda_to_tfda(fda_list, tfda_list))
df["Alert Date"] = pd.to_datetime(df["Alert Date"])

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

# 套用篩選
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

# FDA 官網爬蟲按鈕與結果呈現
st.markdown("### 🔁 抓取並比對 FDA 官網警示")
if st.button("一鍵更新並比對"):
    latest_alerts = fetch_fda_dsc_alerts()
    fda_list_from_web = parse_dsc_to_fda_list(latest_alerts)
    df = pd.DataFrame(match_fda_to_tfda(fda_list_from_web, tfda_list))
    df["Alert Date"] = pd.to_datetime(df["Alert Date"])
    st.session_state["df"] = df

# 若已更新，顯示新結果
if "df" in st.session_state:
    st.markdown("### 📬 最新比對結果")
    st.dataframe(st.session_state["df"], use_container_width=True)
