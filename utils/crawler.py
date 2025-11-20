import requests
from bs4 import BeautifulSoup

def fetch_fda_dsc_alerts():
    url = "https://www.fda.gov/drugs/drug-safety-and-availability/drug-safety-communications"
    resp = requests.get(url)
    print("🔍 HTTP status code:", resp.status_code)
    print("🔍 HTML length:", len(resp.text))

    if resp.status_code != 200:
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    alerts = []
    for item in soup.select(".views-row"):
        title = item.get_text(strip=True)
        link = item.find("a")["href"] if item.find("a") else ""
        alerts.append({"title": title, "link": link})

    print("🔍 抓到的 alerts 數量:", len(alerts))
    return alerts

def parse_dsc_to_fda_list(alerts):
    fda_list = []
    for alert in alerts[:3]:  # 測試版：只取前三筆
        title = alert["title"].lower()
        if "prolia" in title:
            fda_list.append({
                "alert_date": "2025-11-20",
                "source": "DSC",
                "us_product": "Prolia",
                "ingredient": "denosumab",
                "form": "60 mg/1 mL 注射液",
                "risk_summary": "洗腎病人低血鈣風險",
                "action_summary": "建議監測血鈣",
                "fda_excerpt": f"https://www.fda.gov{alert['link']}"
            })
        elif "leqembi" in title:
            fda_list.append({
                "alert_date": "2025-11-20",
                "source": "DSC",
                "us_product": "Leqembi",
                "ingredient": "lecanemab",
                "form": "100 mg/mL 注射液",
                "risk_summary": "APOE ε4 攜帶者 ARIA 風險增加",
                "action_summary": "建議 MRI 監測與基因檢測",
                "fda_excerpt": f"https://www.fda.gov{alert['link']}"
            })
        else:
            fda_list.append({
                "alert_date": "2025-11-20",
                "source": "DSC",
                "us_product": alert["title"],
                "ingredient": "未知",
                "form": "未知",
                "risk_summary": "尚未解析",
                "action_summary": "尚未解析",
                "fda_excerpt": f"https://www.fda.gov{alert['link']}"
            })
    return fda_list

def get_new_alerts():
    latest = fetch_fda_dsc_alerts()
    return latest
