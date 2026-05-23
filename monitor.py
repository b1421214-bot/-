import requests
import os
import time
from datetime import datetime
import pytz

# --- 1. 從 GitHub Secrets 讀取設定 ---
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
    s = requests.Session()
    
    # 設定時區為台北
    tw_tz = pytz.timezone('Asia/Taipei')
    now = datetime.now(tw_tz)
    current_time = now.strftime("%H:%M") # 取得目前小時:分鐘
    
    # 2. 登入 Zuvio
    login_url = "https://irs.zuvio.com.tw/b_irs/login/login_by_mail"
    login_data = {'email': EMAIL, 'password': PWD}
    s.post(login_url, data=login_data)
    
    # 3. 檢查點名狀態
    course_url = f"https://irs.zuvio.com.tw/student_v2/course/rollcall/{MY_COURSE_ID}"
    res = s.get(course_url)
    
    # 4. 判斷邏輯
    if "簽到" in res.text or "點名進行中" in res.text:
        send_dc(f"🚨 偵測到【{TARGET_NAME}】開啟點名！\n系統將於 20 秒後自動簽到...")
        time.sleep(20)
        check_in_url = f"https://irs.zuvio.com.tw/app_v2/check_in/{MY_COURSE_ID}"
        check_res = s.get(check_in_url)
        send_dc(f"✅ 【{TARGET_NAME}】自動簽到執行完畢。\n回傳結果：{check_res.text[:100]}")
        
    else:
        # 如果沒點名，判斷是否快下課了（例如設定在 12:50 - 12:59 之間發送一次總結）
        # 這樣你每週三中午都會收到一則回報，證明系統有在跑
        if "12:50" <= current_time <= "12:59":
            print("下課前最後巡邏，發送結算報告")
            # 為了避免這 10 分鐘內每 5 分鐘噴一次，你可以看 GitHub Actions 的排程頻率
            # 這裡發送一則本日結算
            send_dc(f"📊 本日【{TARGET_NAME}】巡邏結束。自 10:00 起至目前 {current_time} 老師皆未開啟點名。系統運作正常！")
        else:
            print(f"目前時間 {current_time}，尚未偵測到點名。")

if __name__ == "__main__":
    run_monitor()
