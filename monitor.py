import requests
import os
import time
from datetime import datetime, timedelta

# --- 1. 設定區域 ---
EMAIL = os.environ.get('ZUVIO_EMAIL')
PWD = os.environ.get('ZUVIO_PASSWORD')
WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK')

# --- 2. 正式課程清單 ---
# day: 1=週二, 2=週三
COURSES = [
    {
        "name": "GD邏輯思維與運算：運算思維與網頁程式設計(通識多元選修)",
        "id": "1496176", 
        "day": 1,          
        "end_time": "18:55"
    },
    {
        "name": "英語聽講(大學土木2乙)",
        "id": "1496033",
        "day": 2,          
        "end_time": "12:55"
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

    print(f"==== 簽到機器人巡邏中 ====")
    print(f"目前時間：{current_time}")

    s = requests.Session()
    login_url = "https://irs.zuvio.com.tw/b_irs/login/login_by_mail"
    login_data = {'email': EMAIL, 'password': PWD}
    s.post(login_url, data=login_data)
    
    active_monitor = False
    for course in COURSES:
        if current_day == course['day']:
            active_monitor = True
            print(f"📌 監控對象：{course['name']}")
            
            course_url = f"https://irs.zuvio.com.tw/student_v2/course/rollcall/{course['id']}"
            res = s.get(course_url)
            
            # 1. 偵測點名
            if "簽到" in res.text or "點名進行中" in res.text:
                print("🚨 偵測到點名訊號！")
                send_dc(f"🚨 偵測到【{course['name']}】開啟點名！\n系統自動執行中...")
                
                time.sleep(20)
                check_in_url = f"https://irs.zuvio.com.tw/app_v2/check_in/{course['id']}"
                s.get(check_in_url)
                send_dc(f"✅ 【{course['name']}】自動簽到執行完畢。")
                
            # 2. 結算判定
            elif course['end_time'] <= current_time <= (datetime.strptime(course['end_time'], "%H:%M") + timedelta(minutes=10)).strftime("%H:%M"):
                print("📊 偵測到課程結束，發送結算報告。")
                send_dc(f"📊 本日【{course['name']}】監控結束報告：\n目前時間 {current_time}，今日課程期間老師未開啟點名。系統運作正常。")
            
            else:
                print("☕ 尚未偵測到點名，持續監控中...")

    if not active_monitor:
        print("😴 今日目前無監控任務，系統待命。")
    print(f"==== 巡邏任務完成 ====")

if __name__ == "__main__":
    run_monitor()
