def fetch_fda_dsc_current():
    """
    取得 FDA 官網目前 DSC 藥品警訊
    """
    return fetch_fda_dsc_alerts()

def fetch_fda_dsc_alerts():
    url = "https://www.fda.gov/drugs/drug-safety-and-availability/drug-safety-communications"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"❌ FDA 官網連線失敗：{e}")
        return fallback_alerts()

    soup = BeautifulSoup(response.text, "html.parser")
    alert_links = soup.select("a[title]")

    alerts = []
    for tag in alert_links:
        title = tag.get("title", "").strip()
        if not title:
            continue
        product, ingredient = extract_product_and_ingredient(title)
        alerts.append({
            "alert_date": "2025-11-01",  # ⚠️ 暫時無法取得真實日期
            "title": title,
            "source": "DSC",
            "us_product": product,
            "ingredient": ingredient
        })

    if not alerts:
        print("⚠️ FDA 官網解析成功但無警訊資料，啟用 fallback")
        return fallback_alerts()

    return alerts
