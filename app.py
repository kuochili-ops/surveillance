import streamlit as st
import pandas as pd
from difflib import SequenceMatcher

# -------------------------
# 配對模組
# -------------------------
def fuzzy_match(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def compute_match_score(fda, tfda):
    score = 0.0
    # 主成分比對
    if fda["ingredient"] == tfda["ingredient"]:
        score += 0.6
    elif fda["ingredient"].split()[0] == tfda["ingredient"].split()[0]:
        score += 0.5
    # 劑型與規格比對
    if fda["form"] == tfda["form"]:
        score += 0.3
    elif fda["form"].split()[0] == tfda["form"].split()[0]:
        score += 0.2
    # 品名模糊比對
    sim = fuzzy_match(fda["us_product"], tfda["tw_product"])
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
                "FDA Excerpt": fda["fda_excerpt"],
                "TW Link": best_match["tw_link"]
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
                "FDA Excerpt": fda["fda_excerpt"],
                "TW Link": ""
            })
    return results

# -------------------------
# 模擬資料
# -------------------------
fda_list = [
    {
        "alert_date": "2023-04-28",
        "source": "DSC",
        "us_product": "Leqembi",
        "ingredient": "lecanemab",
        "form": "100 mg/mL 注射液",
        "risk_summary": "阿茲海默症 ARIA：APOE ε4 攜帶者風險增加",
        "action_summary": "建議基因檢測",
        "fda_excerpt": "FDA recommends MRI monitoring to reduce ARIA risk, especially in APOE ε4 carriers."
    },
    {
        "alert_date": "2023-04-05",
        "source": "DSC",
        "us_product": "Prolia",
        "ingredient": "denosumab",
        "form": "60 mg/1 mL 注射液",
        "risk_summary": "嚴重低血鈣：洗腎病人風險增加",
        "action_summary": "建議監測血鈣",
        "fda_excerpt": "Risk of severe hypocalcemia in dialysis patients receiving denosumab."
    },
    {
        "alert_date": "2023-03-21",
        "source": "DSC",
        "us_product": "Ocaliva",
        "ingredient": "obeticholic acid",
        "form": "5 mg 錠劑",
        "risk_summary": "原發性膽汁性肝硬化：晚期肝病病人風險增加",
        "action_summary": "建議調整劑量",
        "fda_excerpt": "Serious liver injury reported in non-cirrhotic PBC patients treated with obeticholic acid."
    }
]

tfda_list = [
    {
        "tw_product": "樂意保",
        "ingredient": "lecanemab",
        "form": "100 mg/mL 注射液",
        "license_id": "MOHW-BI-001273",
        "tw_link": "https://lmspiq.fda.gov.tw/web/DRPIQ/DRPIQLicSearch"
    },
    {
        "tw_product": "骨松益",
        "ingredient": "denosumab",
        "form": "60 mg/1 mL 注射液",
        "license_id": "衛部藥製字第XXXX號",
        "tw_link": "https://lmspiq.fda.gov.tw/web/DRPIQ/DRPIQLicSearch"
    }
]

# -------------------------
# 建立 DataFrame
# -------------------------
df = pd.DataFrame(match_fda_to_tfda(fda_list, tfda_list))
df["Alert Date"] = pd.to_datetime(df["Alert Date"])

# -------------------------
# Streamlit UI
# -------------------------
st.set_page_config(page_title="藥品安全警示比對平台", layout="wide")
st.title("藥品安全警示比對平台")

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
    df_filtered = df_filtered[df_filtered.apply(
        lambda row: any(kw in str(row[col]).lower() for col in ["US Product", "Ingredient", "Risk Summary", "Action Summary"]),
        axis=1
    )]

# 主表格
st.subheader("警示列表（已套用篩選）")
if df_filtered.empty:
    st.info("目前篩選條件下沒有資料。請調整日期或關鍵字。")
else:
    display_cols = [
        "Alert Date", "Source", "US Product", "Ingredient",
        "Risk Summary", "Action Summary", "TW Match Status",
        "TW Product", "License ID", "Strength/Form", "Match Confidence"
    ]
    st.dataframe(df_filtered[display_cols], use_container_width=True, hide_index=True)

    # 詳情展開
    for idx, row in df_filtered.iterrows():
        with st.expander(f"詳情｜{row['Alert Date'].date()}｜{row['US Product']}｜{row['Ingredient']}"):
            st.markdown(f"- **風險摘要：** {row['Risk Summary']}")
            st.markdown(f"- **建議行動：** {row['Action Summary']}")
            st.markdown(f"- **FDA 原文片段：** {row['FDA Excerpt']}")
            st.markdown(f"- **來源連結：** [FDA 安全通訊](https://www.fda.gov/drugs/drug-safety-and-availability/drug-safety-communications)")
            if row["TW
