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

