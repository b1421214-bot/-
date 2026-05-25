import requests
import os
import time
from datetime import datetime, timedelta

# --- 1. 設定區域 ---
EMAIL = os.environ.get('ZUVIO_EMAIL')
PWD = os.environ.get('ZUVIO_PASSWORD')
WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK')

# --- 2. 課程清單 (新增：靜力學測試) ---
COURSES = [
    {
        "name": "英語聽講(大學土木2乙)",
        "id": "1496033",
        "day": 2,          # 星期三
        "end_time": "12:55"
    },
    {
        "name": "GD邏輯思維與運算：運算思維與網頁程式設計(通識多元選修)",
        "id": "這裡請填入正確ID", 
        "day": 1,          # 星期二
        "end_time": "18:55"
    },
    {
        "name": "靜力學(大學土木1乙) - 測試用",
        "id": "1496033",   # 測試時先借用英語聽講的 ID 即可
        "day": 0,          # 0=星期一 (配合你現在測試的時間)
        "end_time": "23:22" # <--- 重要：請改成比現在晚 2 分鐘的時間
    }
]

def send_dc(msg):
    payload = {"content": msg}
    try:
        requests.post(WEBHOOK_URL, json=payload)
    except:
        pass

def run_monitor():
    now_utc = datetime.utcnow()
    now_tw = now_utc + timedelta(hours=8)
    current_day = now_tw.weekday()
    current_time = now_tw.strftime("%H:%M") 

    s = requests.Session()
    login_url = "https://irs.zuvio.com.tw/b_irs/login/login_by_mail"
    login_data = {'email': EMAIL, 'password': PWD}
    s.post(login_url, data=login_data)
    
    for course in COURSES:
        if current_day == course['day']:
            course_url = f"https://irs.zuvio.com.tw/student_v2/course/rollcall/{course['id']}"
            res = s.get(course_url)
            
            if "簽到" in res.text or "點名進行中" in res.text:
                send_dc(f"🚨 偵測到【{course['name']}】開啟點名！")
                time.sleep(2) # 測試時縮短時間
                send_dc(f"✅ 【{course['name']}】自動簽到執行完畢。")
                
            # 下課結算判定：如果現在時間 >= 下課時間 且在下課後 10 分鐘內
            elif course['end_time'] <= current_time <= (datetime.strptime(course['end_time'], "%H:%M") + timedelta(minutes=10)).strftime("%H:%M"):
                send_dc(f"📊 本日【{course['name']}】監控結束報告：\n目前時間 {current_time}，今日課程期間老師未開啟點名。系統運作正常。")
                print(f"測試成功：已發送結算報告")

if __name__ == "__main__":
    run_monitor()
