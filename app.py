import streamlit as st
import pandas as pd

# 模擬 FDA ↔ TFDA 比對資料
data = [
    {
        "Alert Date": "2025-08-28",
        "Source": "DSC",
        "US Product": "Leqembi",
        "Ingredient": "lecanemab",
        "Risk Summary": "可能導致 ARIA，APOE ε4 帶原者風險升高",
        "Action Summary": "建議 MRI 監測",
        "TW Match Status": "同主成分",
        "TW Product": "樂意保",
        "License ID": "MOHW-BI-001273",
        "Strength/Form": "100 mg/mL 注射液",
        "Match Confidence": 1.0
    },
    {
        "Alert Date": "2025-06-15",
        "Source": "DSC",
        "US Product": "Prolia",
        "Ingredient": "denosumab",
        "Risk Summary": "透析患者易發生重度低血鈣",
        "Action Summary": "治療前檢測血鈣並補充維生素 D",
        "TW Match Status": "同主成分",
        "TW Product": "骨松益",
        "License ID": "衛部藥製字第XXXX號",
        "Strength/Form": "60 mg/1 mL 注射液",
        "Match Confidence": 0.9
    },
    {
        "Alert Date": "2024-12-12",
        "Source": "DSC",
        "US Product": "Ocaliva",
        "Ingredient": "obeticholic acid",
        "Risk Summary": "非肝硬化 PBC 患者可能出現嚴重肝損傷",
        "Action Summary": "加強肝功能監測，必要時停藥",
        "TW Match Status": "無配對",
        "TW Product": "",
        "License ID": "",
        "Strength/Form": "",
        "Match Confidence": 0.6
    }
]

df = pd.DataFrame(data)

st.title("藥品安全警示比對平台（最小化版本）")
st.dataframe(df, use_container_width=True, hide_index=True)
