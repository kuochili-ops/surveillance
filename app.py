import streamlit as st
import pandas as pd

# 模擬資料（可替換為爬取結果）
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
        "Match Confidence": 1.0,
        "FDA Excerpt": "FDA recommends MRI monitoring to reduce ARIA risk, especially in APOE ε4 carriers.",
        "TW Link": "https://lmspiq.fda.gov.tw/web/DRPIQ/DRPIQLicSearch"
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
        "Match Confidence": 0.9,
        "FDA Excerpt": "Risk of severe hypocalcemia in dialysis patients receiving denosumab.",
        "TW Link": "https://lmspiq.fda.gov.tw/web/DRPIQ/DRPIQLicSearch"
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
        "Match Confidence": 0.6,
        "FDA Excerpt": "Serious liver injury reported in non-cirrhotic PBC patients treated with obeticholic acid.",
        "TW Link": ""
    }
]

df = pd.DataFrame(data)
df["Alert Date"] = pd.to_datetime(df["Alert Date"])

# 頁面設定
st.set_page_config(page_title="藥品安全警示比對平台", layout="wide")
st.title("藥品安全警示比對平台")

# KPI 摘要卡片
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

# 篩選器（Sidebar）
st.sidebar.header("篩選器")
min_date = df["Alert Date"].min().date()
max_date = df["Alert Date"].max().date()
date_range = st.sidebar.date_input("警示日期範圍", value=(min_date, max_date), min_value=min_date, max_value=max_date)
source_options = df["Source"].unique().tolist()
selected_sources = st.sidebar.multiselect("來源類型", options=source_options, default=source_options)
keyword = st.sidebar.text_input("關鍵字搜尋（品名 / 成分 / 摘要）", value="")

# 套用篩選條件
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

# 主表格呈現
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

    # 詳情展開區塊
    for idx, row in df_filtered.iterrows():
        with st.expander(f"詳情｜{row['Alert Date'].date()}｜{row['US Product']}｜{row['Ingredient']}"):
            st.markdown(f"- **風險摘要：** {row['Risk Summary']}")
            st.markdown(f"- **建議行動：** {row['Action Summary']}")
            st.markdown(f"- **FDA 原文片段：** `{row['FDA Excerpt']}`")
            st.markdown(f"- **來源連結：** [FDA 安全通訊](https://www.fda.gov/drugs/drug-safety-and-availability/drug-safety-communications)")
            if row["TW Product"]:
                st.markdown(f"- **台灣許可證：** [{row['TW Product']}（{row['License ID']}）]({row['TW Link']})")
            else:
                st.markdown("- **台灣許可證：** 無同成分或尚未核准")
            st.markdown(f"- **劑型/規格：** {row['Strength/Form'] or '—'}")
            st.markdown(f"- **配對信度：** {row['Match Confidence']:.1f}")

# 匯出功能
csv = df_filtered.to_csv(index=False)
st.download_button("下載 CSV", data=csv, file_name="drug_safety_alerts_filtered.csv", mime="text/csv")
