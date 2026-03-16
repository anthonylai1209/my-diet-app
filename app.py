import streamlit as st
import os
import pandas as pd
from datetime import datetime
import plotly.express as px

# 1. 基礎設定
SAVE_DIR = "uploaded_meals"
LOG_FILE = "weight_log.csv"
if not os.path.exists(SAVE_DIR): os.makedirs(SAVE_DIR)
if not os.path.exists(LOG_FILE):
    df = pd.DataFrame(columns=["時間", "姓名", "體重", "餐點內容"])
    df.to_csv(LOG_FILE, index=False)

st.set_page_config(page_title="我們的減肥大計", page_icon="🥗")

# --- 側邊欄：體重紀錄 ---
with st.sidebar:
    st.header("⚖️ 今日體重回報")
    current_user = st.radio("你是誰？", ["冠瑋", "女友"])
    weight = st.number_input("今日體重 (kg)", min_value=30.0, max_value=150.0, step=0.1)
    if st.button("紀錄體重"):
        new_data = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d"), current_user, weight, "體重紀錄"]], 
                                columns=["時間", "姓名", "體重", "餐點內容"])
        new_data.to_csv(LOG_FILE, mode='a', header=False, index=False)
        st.success("體重已更新！")

# --- 主畫面：飲食上傳 ---
st.title("🥗 冠瑋 & 女友的飲食日誌")

col1, col2 = st.columns(2)
with col1:
    food_desc = st.text_input("這餐吃了什麼？", placeholder="例如：雞胸肉沙拉")
with col2:
    meal_type = st.selectbox("餐別", ["早餐", "午餐", "晚餐", "點心"])

uploaded_file = st.file_uploader("拍張美食照", type=["jpg", "png", "jpeg"])

if st.button("🚀 上傳今日進食紀錄"):
    if uploaded_file and food_desc:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"{timestamp}_{current_user}_{food_desc}.jpg"
        save_path = os.path.join(SAVE_DIR, file_name)
        
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # 同步寫入 CSV 方便後續分析
        log_data = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d %H:%M"), current_user, None, f"[{meal_type}] {food_desc}"]], 
                                columns=["時間", "姓名", "體重", "餐點內容"])
        log_data.to_csv(LOG_FILE, mode='a', header=False, index=False)
        
        st.balloons()
        st.success("紀錄成功！為了更好的身材加油！")
    else:
        st.warning("請填寫內容並上傳照片喔！")

# --- 進階：數據分析看板 ---
st.divider()
tab1, tab2 = st.tabs(["📊 體重趨勢", "📸 飲食牆"])

with tab1:
    st.subheader("體重變化曲線")
    df_plot = pd.read_csv(LOG_FILE)
    df_weight = df_plot[df_plot['體重'].notnull()]
    if not df_weight.empty:
        fig = px.line(df_weight, x="時間", y="體重", color="姓名", markers=True,
                     title="我們的努力看得見", labels={"體重": "體重 (kg)", "時間": "日期"})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("還沒有體重數據，快去秤一下吧！")

with tab2:
    st.subheader("最近的美味紀錄")
    files = sorted(os.listdir(SAVE_DIR), reverse=True)
    if files:
        cols = st.columns(3)
        for idx, file in enumerate(files[:12]): # 顯示最近 12 張
            with cols[idx % 3]:
                st.image(os.path.join(SAVE_DIR, file), use_column_width=True)
                # 檔名解析：20260317_1230_冠瑋_雞肉.jpg
                parts = file.split("_")
                if len(parts) >= 3:
                    st.caption(f"{parts[2]}: {parts[3].split('.')[0]}")
    else:
        st.info("尚無照片紀錄")