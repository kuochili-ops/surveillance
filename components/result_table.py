import streamlit as st

def render_table(df_filtered):
    st.markdown("### 📋 配對結果一覽")
    st.dataframe(df_filtered, use_container_width=True)

def render_details(df_filtered):
    with st.expander("📦 展開每筆警示詳情"):
        for _, row in df_filtered.iterrows():
            st.markdown(f"**🧪 {row['US Product']}**（{row['Ingredient']}）")
            st.markdown(f"- 警示日期：{row['Alert Date'].date()}｜來源：{row['Source']}")
            st.markdown(f"- 台灣配對：{row['TW Match Status']} → `{row['TW Product']}`")
            st.markdown(f"- 摘要：{row['Risk Summary']}")
            st.markdown(f"- 建議：{row['Action Summary']}")
            st.markdown(f"- 詳情：{row['FDA Excerpt']}")
            st.markdown("---")
