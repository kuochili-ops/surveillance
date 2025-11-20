import requests
from bs4 import BeautifulSoup
from datetime import datetime

def fetch_fda_dsc_alerts():
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
                raw_date = date_tag.text.strip()
                normalized_date = normalize_us_date(raw_date)
                alerts.append({
                    "alert_date": normalized_date,
                    "title": title_tag.text.strip(),
                    "source": "DSC"
                })
    return alerts

def normalize_us_date(date_str):
    """
    將美式日期格式 'MM-DD-YYYY' 轉成 'YYYY-MM-DD'
    """
    try:
        dt = datetime.strptime(date_str, "%m-%d-%Y")
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return ""

def parse_dsc_to_fda_list(alerts):
    results = []
    for alert in alerts:
        results.append({
            "alert_date": alert.get("alert_date", ""),
            "source": alert.get("source", "FDA"),
            "us_product": "",          # 可進一步解析
            "ingredient": "",          # 可進一步解析
            "risk_summary": alert.get("title", ""),
            "action_summary": "",
            "fda_excerpt": alert.get("title", "")
        })
    return results

def fetch_fda_dsc_current():
    return fetch_fda_dsc_alerts()
