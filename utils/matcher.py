def match_fda_to_tfda(fda_list, tfda_list):
    """
    將 FDA 藥品警訊與 TFDA 許可證資料比對，並保證輸出欄位完整。
    即使沒有比對成功或資料缺漏，也會填入空字串。
    """

    results = []

    for fda in fda_list:
        # 嘗試比對 TFDA（這裡簡化為名稱比對，你可以依需求改進）
        matched_tfda = None
        if tfda_list:
            for tfda in tfda_list:
                if fda.get("ingredient", "").lower() == tfda.get("ingredient", "").lower():
                    matched_tfda = tfda
                    break

        results.append({
            # 保證欄位完整
            "Alert Date": fda.get("alert_date", ""),
            "Source": fda.get("source", "FDA"),
            "US Product": fda.get("us_product", ""),
            "Ingredient": fda.get("ingredient", ""),
            "Risk Summary": fda.get("risk_summary", ""),
            "Action Summary": fda.get("action_summary", ""),
            "FDA Excerpt": fda.get("fda_excerpt", ""),
            "TFDA License": matched_tfda.get("license_no", "") if matched_tfda else "",
            "TFDA Product": matched_tfda.get("product_name", "") if matched_tfda else "",
        })

    return results
