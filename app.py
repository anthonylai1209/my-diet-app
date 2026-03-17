import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import plotly.express as px
import os

# 1. 基礎設定與 Google Sheets 連線
st.set_page_config(page_title="我們的減肥大計", page_icon="🥗")
SAVE_DIR = "uploaded_meals"
if not os.path.exists(SAVE_DIR): os.makedirs(SAVE_DIR)

# 建立 Google Sheets 連線
# 請在 Streamlit Cloud 的 Secrets 設定中貼上你的 Google Sheet 網址
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("🥗 冠瑋 & 柯彤的雲端日誌")

# --- 側邊欄：體重紀錄 ---
with st.sidebar:
    st.header("⚖️ 今日體重回報")
    current_user = st.radio("你是誰？", ["冠瑋", "柯彤"])
    weight = st.number_input("今日體重 (kg)", min_value=30.0, max_value=150.0, step=0.1)
    if st.button("紀錄體重"):
        # 抓取現有資料
        existing_data = conn.read(worksheet="Sheet1")
        new_row = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d"), current_user, weight, "體重紀錄"]], 
                                columns=["時間", "姓名", "體重", "餐點內容"])
        updated_df = pd.concat([existing_data, new_row], ignore_index=True)
        conn.update(worksheet="Sheet1", data=updated_df)
        st.success("體重已同步至 Google Sheets！")

# --- 主畫面：飲食上傳 ---
food_desc = st.text_input("這餐吃了什麼？")
uploaded_file = st.file_uploader("拍張照片", type=["jpg", "png", "jpeg"])

if st.button("🚀 上傳紀錄"):
    if food_desc:
        # 寫入文字到 Google Sheets
        existing_data = conn.read(worksheet="Sheet1")
        new_row = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d %H:%M"), current_user, None, food_desc]], 
                                columns=["時間", "姓名", "體重", "餐點內容"])
        updated_df = pd.concat([existing_data, new_row], ignore_index=True)
        conn.update(worksheet="Sheet1", data=updated_df)
        
        # 儲存照片 (暫存在伺服器)
        if uploaded_file:
            with open(os.path.join(SAVE_DIR, f"{datetime.now().strftime('%Y%m%d')}_{current_user}.jpg"), "wb") as f:
                f.write(uploaded_file.getbuffer())
        
        st.balloons()
        st.success("紀錄已存入雲端表格！")

# --- 數據分析 ---
st.divider()
try:
    df = conn.read(worksheet="Sheet1")
    df_weight = df[df['體重'].notnull()]
    if not df_weight.empty:
        fig = px.line(df_weight, x="時間", y="體重", color="姓名", markers=True)
        st.plotly_chart(fig)
except:
    st.info("點擊紀錄後將自動產生圖表")
