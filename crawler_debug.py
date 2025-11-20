import streamlit as st
import requests
from bs4 import BeautifulSoup

url = "https://www.fda.gov/drugs/drug-safety-and-availability/drug-safety-communications"
headers = {"User-Agent": "Mozilla/5.0"}
response = requests.get(url, headers=headers, timeout=10)

if response.status_code == 200:
    st.success("✅ FDA 官網連線成功")
    soup = BeautifulSoup(response.text, "html.parser")
    section = soup.find("div", class_="view-content")

    if section:
        st.success("✅ 成功找到 view-content 區塊")
        st.code(str(section)[:3000], language="html")  # 顯示前 3000 字元
    else:
        st.error("❌ 找不到 view-content 區塊，可能 FDA 官網結構已變")
        st.code(response.text[:3000], language="html")
else:
    st.error(f"❌ FDA 官網連線失敗，狀態碼：{response.status_code}")
