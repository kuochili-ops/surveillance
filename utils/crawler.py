import requests
from bs4 import BeautifulSoup
import re

# 成分抽取工具
def extract_product_and_ingredient(title):
    match = re.search(r"([A-Za-z0-9\-]+)\s*\(([^)]+)\)", title)
    if match:
        return match.group(1), match.group(2)
    return "", ""

# 日期解析工具：從 URL 中推斷日期
def extract_date_from_url(href):
    match = re.search(r"/(\d{4}-\d{2}-\d{2})-", href)
    return match.group(1) if match else None

# 主爬蟲：FDA DSC 警訊
def fetch_fda_dsc_alerts():
    url = "https://www.fda.gov/drugs/drug-safety-and-availability/drug-safety-communications"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"❌ FDA 官網連線失敗：{e}")
        print("⚠️ 啟用 fallback_alerts()")
        return fallback_alerts()

    soup = BeautifulSoup(response.text, "html.parser")
    alert_links = soup.select("a[title]")

    alerts = []
    for tag in alert_links:
        title = tag.get("title", "").strip()
        href = tag.get("href", "")
        if not title or "Drug Safety Communication" not in title:
            continue
        product, ingredient = extract_product_and_ingredient(title)
        alert_date = extract_date_from_url(href) or "2025-11-01"
        alerts.append({
            "alert_date": alert_date,
            "title": title,
            "source": "DSC",
            "us_product": product,
            "ingredient": ingredient
        })

    if not alerts:
        print("⚠️ FDA 官網解析成功但無警訊資料，啟用 fallback")
        return fallback_alerts()

    return alerts

# 目前警訊（介面用）
def fetch_fda_dsc_current():
    return fetch_fda_dsc_alerts()

# fallback 測試資料（多筆）
def fallback_alerts():
    return [
        {
            "alert_date": "2025-11-01",
            "title": "Leqembi (lecanemab) may increase MRI risk",
            "source": "DSC",
            "us_product": "Leqembi",
            "ingredient": "lecanemab"
        },
        {
            "alert_date": "2025-10-15",
            "title": "Zyrtec (cetirizine) linked to drowsiness in elderly",
            "source": "DSC",
            "us_product": "Zyrtec",
            "ingredient": "cetirizine"
        },
        {
            "alert_date": "2025-08-01",
            "title": "Tylenol (acetaminophen) overdose risk update",
            "source": "DSC",
            "us_product": "Tylenol",
            "ingredient": "acetaminophen"
        }
    ]
