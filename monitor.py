import requests
import os
import time
from datetime import datetime, timedelta

# --- 1. 從 GitHub Secrets 讀取設定 ---
EMAIL = os.environ.get('ZUVIO_EMAIL')
PWD = os.environ.get('ZUVIO_PASSWORD')
WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK')

# --- 2. 課程清單 (新增：GD邏輯思維與運算) ---
# day: 0=週一, 1=週二, 2=週三, 3=週四, 4=週五
COURSES = [
    {
        "name": "英語聽講(大學土木2乙)",
        "id": "1496033",
        "day": 2,          # 星期三
        "end_time": "12:55"
    },
    {
        "name": "GD邏輯思維與運算：運算思維與網頁程式設計(通識多元選修)",
        "id": "請在此填入新課程的ID", # <--- 重要：請至 Zuvio 網址列查看並替換
        "day": 1,          # 星期二
        "end_time": "18:55"
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

    s = requests.Session()
    # 登入 Zuvio
    login_url = "https://irs.zuvio.com.tw/b_irs/login/login_by_mail"
    login_data = {'email': EMAIL, 'password': PWD}
    s.post(login_url, data=login_data)
    
    # 遍歷課程清單
    for course in COURSES:
        # 只在該課程對應的星期幾執行
        if current_day == course['day']:
            course_url = f"https://irs.zuvio.com.tw/student_v2/course/rollcall/{course['id']}"
            res = s.get(course_url)
            
            # 偵測點名關鍵字
            if "簽到" in res.text or "點名進行中" in res.text:
                send_dc(f"🚨 偵測到【{course['name']}】開啟點名！\n系統將於 20 秒後自動執行簽到作業...")
                time.sleep(20)
                check_in_url = f"https://irs.zuvio.com.tw/app_v2/check_in/{course['id']}"
                check_res = s.get(check_in_url)
                send_dc(f"✅ 【{course['name']}】自動簽到執行完畢。\n結果：{check_res.text[:100]}")
                
            # 下課結算判定 (在下課時間後的 10 分鐘內觸發)
            elif course['end_time'] <= current_time <= (datetime.strptime(course['end_time'], "%H:%M") + timedelta(minutes=10)).strftime("%H:%M"):
                send_dc(f"📊 本日【{course['name']}】監控結束報告：\n課程期間皆未開啟點名。系統運作正常。")
                print(f"{course['name']} 結算發送完畢。")

if __name__ == "__main__":
    run_monitor()
