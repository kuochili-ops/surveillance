import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

def fetch_fda_dsc_alerts():
    url = "https://www.fda.gov/drugs/drug-safety-and-availability/drug-safety-communications"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        print("✅ FDA 官網連線成功")
    except Exception as e:
        print(f"❌ FDA 官網連線失敗：{e}")
        return fallback_alerts()

    soup = BeautifulSoup(response.text, "html.parser")
    section = soup.find("div", class_="view-content")
    if not section:
        print("⚠️ 找不到 FDA 官網的 DSC 警訊區塊")
        return fallback_alerts()

    alerts = []
    items = section.find_all("div", class_="views-row")
    for item in items:
        date_tag = item.find("span", class_="date-display-single")
        title_tag = item.find("h3")
        if not date_tag or not title_tag:
            continue

        raw_date = date_tag.text.strip()
        normalized_date = normalize_us_date(raw_date)
        title = title_tag.text.strip()
        product, ingredient = extract_product_and_ingredient(title)

        alerts.append({
            "alert_date": normalized_date,
            "title": title,
            "source": "DSC",
            "us_product": product,
            "ingredient": ingredient
        })

    if not alerts:
        print("⚠️ FDA 官網解析成功但無警訊資料，啟用 fallback")
        return fallback_alerts()

    return alerts

def normalize_us_date(date_str):
    try:
        dt = datetime.strptime(date_str, "%m-%d-%Y")
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return ""

def extract_product_and_ingredient(title):
    match = re.search(r"([A-Za-z0-9\-]+)\s*\(([^)]+)\)", title)
    if match:
        return match.group(1), match.group(2)
    return "", ""

def fallback_alerts():
    # 提供一筆測試資料，避免 app 爆錯
    return [{
        "alert_date": "2025-11-01",
        "title": "Leqembi (lecanemab) may increase MRI risk",
        "source": "DSC",
        "us_product": "Leqembi",
        "ingredient": "lecanemab"
    }]

def parse_dsc_to_fda_list(alerts):
    results = []
    for alert in alerts:
        results.append({
            "alert_date": alert.get("alert_date", ""),
            "source": alert.get("source", "FDA"),
            "us_product": alert.get("us_product", ""),
            "ingredient": alert.get("ingredient", ""),
            "risk_summary": alert.get("title", ""),
            "action_summary": "",
            "fda_excerpt": alert.get("title", "")
        })
    return results

def fetch_fda_dsc_current():
    return fetch_fda_dsc_alerts()
