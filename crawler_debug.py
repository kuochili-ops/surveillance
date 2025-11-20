import streamlit as st
import requests
from bs4 import BeautifulSoup
from utils.crawler import fetch_fda_dsc_alerts

st.set_page_config(page_title="FDA 官網爬蟲診斷工具", layout="wide")
st.title("🧪 FDA 官網爬蟲診斷工具")

# 抓取警訊資料
alerts = fetch_fda_dsc_alerts()
st.write(f"📦 共抓到 {len(alerts)} 筆 FDA DSC 警訊")

# 顯示前幾筆警訊
if alerts:
    st.subheader("🔔 前 5 筆警訊資料")
    st.table(alerts[:5])
else:
    st.error("❌ 沒有抓到任何警訊，可能啟用了 fallback 或爬蟲失敗")

# 顯示原始 HTML 結構診斷
st.subheader("🔍 FDA 官網 HTML 結構診斷")

url = "https://www.fda.gov/drugs/drug-safety-and-availability/drug-safety-communications"
headers = {"User-Agent": "Mozilla/5.0"}

try:
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    # 顯示 view-content 區塊（或其他主要容器）
    section = soup.find("div", class_="view-content")
    if section:
        st.success("✅ 成功找到 view-content 區塊")
        st.code(str(section)[:3000], language="html")
    else:
        st.warning("⚠️ 找不到 view-content 區塊，可能 FDA 官網結構已變")
        st.code(response.text[:3000], language="html")

except Exception as e:
    st.error(f"❌ FDA 官網連線失敗：{e}")
