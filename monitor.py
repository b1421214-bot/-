import requests
import os
import time

# --- 設定區域 ---
EMAIL = os.environ.get('ZUVIO_EMAIL')
PWD = os.environ.get('ZUVIO_PASSWORD')
WEBHOOK_URL = os.environ.get('WEBHOOK_URL')

MY_COURSE_ID = "1496033"
TARGET_NAME = "英語聽講(大學土木2乙)"

def send_dc(msg):
    payload = {"content": msg}
    requests.post(WEBHOOK_URL, json=payload)

def run_monitor():
    s = requests.Session()
    
    # 1. 登入
    login_url = "https://irs.zuvio.com.tw/b_irs/login/login_by_mail"
    login_data = {'email': EMAIL, 'password': PWD}
    s.post(login_url, data=login_data)
    
    # 2. 獲取課程頁面
    course_url = f"https://irs.zuvio.com.tw/student_v2/course/rollcall/{MY_COURSE_ID}"
    res = s.get(course_url)
    
    # 3. 判斷邏輯
    if "簽到" in res.text or "點名進行中" in res.text:
        send_dc(f"🚨 偵測到【{TARGET_NAME}】開啟點名！")
        time.sleep(20)
        check_in_url = f"https://irs.zuvio.com.tw/app_v2/check_in/{MY_COURSE_ID}"
        check_res = s.get(check_in_url)
        send_dc(f"✅ 自動簽到執行完畢。回傳結果：{check_res.text[:100]}")
    else:
        # 現在不是上課時間，執行後會跑這一段
        print("目前沒有點名中")
        send_dc(f"系統巡邏中：目前【{TARGET_NAME}】沒有點名。")

if __name__ == "__main__":
    run_monitor()
