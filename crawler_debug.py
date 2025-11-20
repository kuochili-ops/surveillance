from utils.crawler import fetch_fda_dsc_alerts
from pprint import pprint

alerts = fetch_fda_dsc_alerts()

print(f"\n📦 共抓到 {len(alerts)} 筆 FDA DSC 警訊\n")
for i, alert in enumerate(alerts[:5], 1):  # 顯示前 5 筆
    print(f"🔔 第 {i} 筆")
    pprint(alert)
