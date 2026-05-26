import requests
import os
import time
from datetime import datetime, timedelta

# --- 1. 設定區域 ---
EMAIL = os.environ.get('ZUVIO_EMAIL')
PWD = os.environ.get('ZUVIO_PASSWORD')
WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK')

# --- 2. 正式課程清單 ---
COURSES = [
    {
        "name": "GD邏輯思維與運算：運算思維與網頁程式設計(通識多元選修)",
        "id": "你的7位數ID", # 請確認這裡已填入
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
        r = requests.post(WEBHOOK_URL, json=payload)
        print(f"Discord 通知狀態: {r.status_code}")
    except Exception as e:
        print(f"Discord 發送失敗: {e}")

def run_monitor():
    # 強制使用台北時間 (UTC+8)
    now_tw = datetime.utcnow() + timedelta(hours=8)
    current_day = now_tw.weekday()
    current_time = now_tw.strftime("%H:%M") 

    print(f"==== 巡邏系統啟動 ====")
    print(f"目前台北時間：{current_time} (星期代碼: {current_day})")

    s = requests.Session()
    login_url = "https://irs.zuvio.com.tw/b_irs/login/login_by_mail"
    login_data = {'email': EMAIL, 'password': PWD}
    
    try:
        login_res = s.post(login_url, data=login_data)
        if "登入成功" in login_res.text or login_res.status_code == 200:
            print("Zuvio 登入連線正常")
    except:
        print("連線至 Zuvio 失敗")

    active_monitor = False
    for course in COURSES:
        if current_day == course['day']:
            active_monitor = True
            print(f"📌 正在檢查：{course['name']}")
            
            # 偵測點名
            course_url = f"https://irs.zuvio.com.tw/student_v2/course/rollcall/{course['id']}"
            res = s.get(course_url)
            
            if "簽到" in res.text or "點名進行中" in res.text:
                print("🚨 發現點名訊號！")
                send_dc(f"🚨 偵測到【{course['name']}】開啟點名！正在執行自動簽到...")
                time.sleep(10)
                s.get(f"https://irs.zuvio.com.tw/app_v2/check_in/{course['id']}")
                send_dc(f"✅ 【{course['name']}】自動簽到完成。")
            
            # 結算報告：若目前時間在 end_time 之後，且在 19:30 之前，就發送報告
            elif course['end_time'] <= current_time <= "19:30":
                print("📊 偵測到下課時間，準備發送結算報告...")
                send_dc(f"📊 本日【{course['name']}】監控結束報告：\n課程已於 {course['end_time']} 結束。監控期間未偵測到點名，系統運作正常。")
            
            else:
                print("☕ 尚未偵測到點名，持續守候中。")

    if not active_monitor:
        print("😴 今日目前時段無監控任務。")
    print(f"==== 巡邏結束 ====")

if __name__ == "__main__":
    run_monitor()
