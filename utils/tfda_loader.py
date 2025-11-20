import json

def load_tfda_data(path="data/tfda.json"):
    """載入 TFDA 許可證資料"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            tfda_list = json.load(f)
        print(f"✅ 成功載入 TFDA 資料，共 {len(tfda_list)} 筆")
        return tfda_list
    except Exception as e:
        print("⚠️ 載入 TFDA 資料失敗：", e)
        return []
