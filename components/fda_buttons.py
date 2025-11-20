import streamlit as st
import pandas as pd
from utils.crawler import fetch_fda_dsc_alerts, parse_dsc_to_fda_list, get_new_alerts
from utils.matcher import match_fda_to_tfda

def render_fda_buttons(tfda_list):
    # 一鍵抓取並比對 FDA 官網警示
    st.markdown("### 🔁 一鍵抓取並比對 FDA 官網警示")
    if st.button("立即更新"):
        alerts = fetch_fda_dsc_alerts()
        fda_list = parse_dsc_to_fda_list(alerts)
        df_web = pd.DataFrame(match_fda_to_tfda(fda_list, tfda_list))

        if not df_web.empty and "Alert Date" in df_web.columns:
            df_web["Alert Date"] = pd.to_datetime(df_web["Alert Date"])
            st.dataframe(df_web, use_container_width=True)
        else:
            st.warning("⚠️ 官網警示比對失敗或資料格式異常。")

    # 檢查是否有新警示
    st.markdown("### 🔍 檢查 FDA 官網是否有新警示")
    if st.button("檢查新警示並比對"):
        new_alerts = get_new_alerts()
        if new_alerts:
            fda_list_new = parse_dsc_to_fda_list(new_alerts)
            df_new = pd.DataFrame(match_fda_to_tfda(fda_list_new, tfda_list))

            if not df_new.empty and "Alert Date" in df_new.columns:
                df_new["Alert Date"] = pd.to_datetime(df_new["Alert Date"])
                st.dataframe(df_new, use_container_width=True)
            else:
                st.warning("⚠️ 新警示資料格式異常，無法顯示。")
        else:
            st.info("目前沒有新警示。")
