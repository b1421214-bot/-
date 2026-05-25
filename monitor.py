import requests
import os
import time
from datetime import datetime, timedelta

# --- 1. 從 GitHub Secrets 讀取設定 ---
EMAIL = os.environ.get('ZUVIO_EMAIL')
PWD = os.environ.get('ZUVIO_PASSWORD')
WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK')

# --- 2. 課程清單 (包含靜力學測試) ---
COURSES = [
    {
        "name": "英語聽講(大學土木2乙)",
        "id": "1496033",
        "day": 2,          # 星期三
        "end_time": "12:55"
    },
    {
        "name": "GD邏輯思維與運算：運算思維與網頁程式設計(通識多元選修)",
        "id": "請填入正確ID", 
        "day": 1,          # 星期二
        "end_time": "18:55"
    },
    {
        "name": "靜力學(大學土木1乙)",
        "id": "1496033",   # 測試用 ID
        "day": 0,          # 星期一 (現在)
        "end_time": "23:30" # 23:30 開始進入結算判定
    }
]

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
    current_day = now_tw.weekday()
    current_time = now_tw.strftime("%H:%M") 

    print(f"目前伺服器時間：{current_time}，星期：{current_day}")

    s = requests.Session()
    login_url = "https://irs.zuvio.com.tw/b_irs/login/login_by_mail"
    login_data = {'email': EMAIL, 'password': PWD}
    s.post(login_url, data=login_data)
    
    for course in COURSES:
        # 1. 檢查是否為該課程的星期
        if current_day == course['day']:
            course_url = f"https://irs.zuvio.com.tw/student_v2/course/rollcall/{course['id']}"
            res = s.get(course_url)
            
            # 2. 優先判斷是否正在點名
            if "簽到" in res.text or "點名進行中" in res.text:
                send_dc(f"🚨 偵測到【{course['name']}】開啟點名！\n系統將於 20 秒後自動執行簽到作業...")
                time.sleep(20)
                check_in_url = f"https://irs.zuvio.com.tw/app_v2/check_in/{course['id']}"
                check_res = s.get(check_in_url)
                send_dc(f"✅ 【{course['name']}】自動簽到執行完畢。")
                
            # 3. 判斷是否為結算時間 (現在時間 >= 下課時間)
            elif current_time >= course['end_time']:
                # 為了避免重複發送，我們在日誌記錄，並發送到 Discord
                send_dc(f"📊 本日【{course['name']}】監控結束報告：\n目前時間 {current_time}，今日課程期間老師未開啟點名。系統運作正常。")
                print(f"{course['name']} 結算成功！")

if __name__ == "__main__":
    run_monitor()
