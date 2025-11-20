import requests
from bs4 import BeautifulSoup

def fetch_fda_dsc_alerts():
    # 原始 DSC RSS 或 JSON 來源（依你原本的設計）
    # 這裡保留原始爬蟲邏輯
    return []

def parse_dsc_to_fda_list(alerts):
    # 將 alerts 轉成標準格式
    return []

def fetch_fda_dsc_current():
    url = "https://www.fda.gov/drugs/drug-safety-and-availability/drug-safety-communications"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    alerts = []
    section = soup.find("div", {"class": "view-content"})
    if section:
        items = section.find_all("div", {"class": "views-row"})
        for item in items:
            date_tag = item.find("span", {"class": "date-display-single"})
            title_tag = item.find("h3")
            if date_tag and title_tag:
                alerts.append({
                    "Date": date_tag.text.strip(),
                    "Title": title_tag.text.strip()
                })
    return alerts
