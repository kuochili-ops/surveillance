import requests
from bs4 import BeautifulSoup
import json
import os

FDA_URL = "https://www.fda.gov/drugs/drug-safety-and-availability/drug-safety-communications"
CACHE_PATH = "data/fda_cache.json"

def fetch_fda_dsc_alerts():
    """抓取 FDA 官網 Drug Safety Communications 頁面，回傳 alerts 清單"""
    try:
        resp = requests.get(FDA_URL, timeout=10)
        if resp.status_code != 200:
            print("⚠️ FDA 官網連線失敗，狀態碼：", resp.status_code)
            return []

        soup = BeautifulSoup(resp.text, "html.parser")

        alerts = []
        # 抓取每篇 DSC 的標題與連結
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
    """將 alerts 轉換成標準化的 fda_list 結構"""
    if not alerts:
        print("⚠️ 警示清單為空，使用備援資料")
        from utils.fallback_data import fda_list
        return fda_list

    fda_list = []
    for alert in alerts:
        fda_list.append({
            "alert_date": "",  # 官網需進一步解析日期，可擴充
            "source": "FDA",
            "us_product": alert["title"],
            "ingredient": "未知",
            "form": "未知",
            "risk_summary": "尚未解析，請參考 FDA 原文",
            "action_summary": "尚未解析，請參考 FDA 原文",
            "fda_excerpt": f"https://www.fda.gov{alert['link']}"
        })

    print("✅ 成功轉換 fda_list 數量：", len(fda_list))
    return fda_list

def get_new_alerts():
    """比對快取，回傳新警示"""
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
