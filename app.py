import streamlit as st
import pandas as pd

# -------------------------
# 模擬資料（可替換為爬取結果）
# -------------------------
data = [
    {
        "Alert Date": "2023-04-28",
        "Source": "DSC",
        "US Product": "Leqembi",
        "Ingredient": "lecanemab",
        "Risk Summary": "阿茲海默症 ARIA：APOE ε4 攜帶者風險增加",
        "Action Summary": "建議基因檢測",
        "TW Match Status": "同主成分",
        "TW Product": "樂意保",
        "License ID": "MOHW-BI-001273",
        "Strength/Form": "100 mg/mL 注射液",
        "Match Confidence": 1.0
    },
    {
        "Alert Date": "2023-04-05",
        "Source": "DSC",
        "US Product": "Prolia",
        "Ingredient": "denosumab",
        "Risk Summary": "嚴重低血鈣：洗腎病人風險增加",
        "Action Summary": "建議監測血鈣",
        "TW Match Status": "同主成分",
        "TW Product": "骨松益",
        "License ID": "衛部藥製字第XXXX號",
        "Strength/Form": "60 mg/1 mL 注射液",
        "Match Confidence": 0.9
    },
    {
        "Alert Date": "2023-03-21",
        "Source": "DSC",
        "US Product": "Ocaliva",
        "Ingredient": "obeticholic acid",
        "Risk Summary": "原發性膽汁性肝硬化：晚期肝病病人風險增加",
        "Action Summary": "建議調整劑量",
        "TW Match Status": "無配對",
        "TW Product": "",
        "License ID": "",
        "Strength/Form": "",
        "Match Confidence": 0.6
    }
]

df = pd.DataFrame(data)

# -------------------------
# 頁面設定
# -------------------------
st.set_page_config(page_title="藥品安全警示比對平台", layout="wide")
st.title("藥品安全警示比對平台")

# -------------------------
# KPI 摘要卡片
# -------------------------
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="本期警示數", value=len(df))
with col2:
    boxed_count = 1  # 假設本期有 1 筆黑框警語
    st.metric(label="新增黑框警語數", value=boxed_count)
with col3:
    matched_count = (df["TW Match Status"] != "無配對").sum()
    st.metric(label="台灣有配對藥品數", value
