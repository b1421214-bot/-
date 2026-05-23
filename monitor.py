import requests
import os
import time
from datetime import datetime, timedelta

# --- 1. 設定區域 ---
EMAIL = os.environ.get('ZUVIO_EMAIL')
PWD = os.environ.get('ZUVIO_PASSWORD')
WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK')

MY_COURSE_ID = "1496033"
TARGET_NAME = "英語聽講(大學土木2乙)"

def send_dc(msg):
    payload = {"content": msg}
    try:
        requests.post(WEBHOOK_URL, json=payload)
    except:
        pass

def run_monitor():
    # 取得台北時間 (UTC+8)
    now_utc = datetime.utcnow()
    now_tw = now_utc + timedelta(hours=8)
    current_time = now_tw.strftime("%H:%M") 

    s = requests.Session()
    
    # 2. 登入 Zuvio
    login_url = "https://irs.zuvio.com.tw/b_irs/login/login_by_mail"
    login_data = {'email': EMAIL, 'password': PWD}
    s.post(login_url, data=login_data)
    
    # 3. 獲取課程頁面
    course_url = f"https://irs.zuvio.com.tw/student_v2/course/rollcall/{MY_COURSE_ID}"
    res = s.get(course_url)
    
    # 4. 判斷邏輯
    if "簽到" in res.text or "點名進行中" in res.text:
        # --- A. 偵測到點名動作 ---
        send_dc(f"🚨 偵測到【{TARGET_NAME}】開啟點名！\n系統將於 20 秒後自動執行簽到作業...")
        time.sleep(20)
        
        check_in_url = f"https://irs.zuvio.com.tw/app_v2/check_in/{MY_COURSE_ID}"
        check_res = s.get(check_in_url)
        send_dc(f"✅ 【{TARGET_NAME}】自動簽到執行完畢。\n回傳結果：{check_res.text[:100]}")
        
    elif "12:50" <= current_time <= "13:00":
        # --- B. 下課結算動作 (只有在週三中午會觸發一次) ---
        # 這樣可以確保在課程結束前，你會收到一則系統活著的證明
        send_dc(f"📊 本日【{TARGET_NAME}】巡邏結束報告：\n目前時間 {current_time}，今日課程期間老師未開啟點名。系統監控正常。")
        print("已發送下課結算報告。")
        
    else:
        # --- C. 平時巡邏 (安靜模式) ---
        print(f"目前時間 {current_time}，尚未偵測到點名，持續監控中...")

if __name__ == "__main__":
    run_monitor()
