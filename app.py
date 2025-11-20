import streamlit as st
import pandas as pd
from utils.matcher import match_fda_to_tfda
from utils.crawler import fetch_fda_dsc_alerts, parse_dsc_to_fda_list, get_new_alerts
from components.kpi_cards import render_kpi
from components.filters import apply_filters
from components.result_table import render_table, render_details
from components.fda_buttons import render_fda_buttons

# 預設 FDA 清單（可移至 crawler.py 作為 fallback）
from utils.fallback_data import fda_list

# Streamlit 主畫面
st.set_page_config(page_title="藥品安全警示比對平台", layout="wide")
st.title("藥品安全警示比對平台")

# 讀取 TFDA 許可證清單
try:
    df_tfda = pd.read_csv("data/37_2b.csv")
    required_cols = ["tw_product", "ingredient", "form", "license_id"]
    if not all(col in df_tfda.columns for col in required_cols):
        st.error("❌ 37_2b.csv 欄位缺漏，請確認包含：tw_product, ingredient, form, license_id")
        tfda_list = []
    else:
        tfda_list = df_tfda[required_cols].to_dict(orient="records")
except Exception as e:
    st.error(f"❌ 讀取 TFDA 許可證失敗：{e}")
    tfda_list = []

# 執行配對
df = pd.DataFrame(match_fda_to_tfda(fda_list, tfda_list))
if df.empty:
    st.error("⚠️ 沒有配對結果，請確認 TFDA 資料與 FDA 清單格式。")
    st.stop()
df["Alert Date"] = pd.to_datetime(df["Alert Date"])

# KPI 卡片
render_kpi(df)

# 篩選器與主表格
df_filtered = apply_filters(df)
render_table(df_filtered)
render_details(df_filtered)

# FDA 官網互動按鈕
render_fda_buttons(tfda_list)
