import requests
from bs4 import BeautifulSoup
import json
import os

FDA_URL = "https://www.fda.gov/drugs/drug-safety-and-availability/drug-safety-communications"
CACHE_PATH = "data/fda_cache.json"

def fetch_fda_dsc_alerts():
    try:
        resp = requests.get(FDA_URL, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")

        # 改用更穩定的選擇器
        alerts = []
        for item in soup.select("div.views-row a"):
            title = item.get_text(strip=True)
            link = item.get("href", "")
            if title and link:
                alerts.append({"title": title, "link": link})

        print("✅ 成功抓取 FDA 警示數量：", len(alerts))
        return alerts

    except Exception as e:
        print("❌ 抓取 FDA 官網失敗：", e)
        return []

def parse_dsc_to_fda_list(alerts):
    if not alerts:
        print("⚠️ 警示清單為空，使用備援資料")
        from utils.fallback_data import fda_list
        return fda_list

    fda_list = []
    for alert in alerts[:3]:  # 測試版：只取前三筆
        title = alert["title"].lower()
        if "prolia" in title:
            fda_list.append({
                "alert_date": "2025-11-01",
                "source": "FDA",
                "us_product": "Prolia",
                "ingredient": "denosumab",
                "form": "60 mg/1 mL 注射液",
                "risk_summary": "Severe hypocalcemia in dialysis patients",
                "action_summary": "Monitor calcium levels",
                "fda_excerpt": f"https://www.fda.gov{alert['link']}"
            })
        elif "leqembi" in title:
            fda_list.append({
                "alert_date": "2025-11-01",
                "source": "FDA",
                "us_product": "Leqembi",
                "ingredient": "lecanemab",
                "form": "100 mg/mL 注射液",
                "risk_summary": "Increased risk of brain swelling and bleeding",
                "action_summary": "FDA recommends genetic testing for APOE ARIA risk",
                "fda_excerpt": f"https://www.fda.gov{alert['link']}"
            })
        elif "jynarque" in title:
            fda_list.append({
                "alert_date": "2025-11-01",
                "source": "FDA",
                "us_product": "Jynarque",
                "ingredient": "tolvaptan",
                "form": "30 mg 錠劑",
                "risk_summary": "Liver injury",
                "action_summary": "Monitor liver function",
                "fda_excerpt": f"https://www.fda.gov{alert['link']}"
            })
        else:
            fda_list.append({
                "alert_date": "2025-11-01",
                "source": "FDA",
                "us_product": alert["title"],
                "ingredient": "未知",
                "form": "未知",
                "risk_summary": "尚未解析",
                "action_summary": "請參考 FDA 原文摘要",
                "fda_excerpt": f"https://www.fda.gov{alert['link']}"
            })

    print("✅ 成功解析 fda_list 數量：", len(fda_list))
    return fda_list

def get_new_alerts():
    latest = fetch_fda_dsc_alerts()
    latest_titles = {a["title"] for a in latest}

    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, "r", encoding="utf-8") as f:
            cached = json.load(f)
        cached_titles = {a["title"] for a in cached}
    else:
        cached_titles = set()

    new_titles = latest_titles - cached_titles
    new_alerts = [a for a in latest if a["title"] in new_titles]

    # 更新快取
    try:
        with open(CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(latest, f, ensure_ascii=False, indent=2)
        print("✅ 快取已更新")
    except Exception as e:
        print("⚠️ 快取更新失敗：", e)

    print(f"🔍 新警示數量：{len(new_alerts)}")
    return new_alerts
