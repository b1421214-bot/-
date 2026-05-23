import requests
import os
import time

# --- 1. 從 GitHub Secrets 讀取設定 ---
EMAIL = os.environ.get('ZUVIO_EMAIL')
PWD = os.environ.get('ZUVIO_PASSWORD')
WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK')

# 你的目標課程資訊
MY_COURSE_ID = "1496033"
TARGET_NAME = "英語聽講(大學土木2乙)"

def send_dc(msg):
    """將訊息傳送到 Discord"""
    payload = {"content": msg}
    try:
        requests.post(WEBHOOK_URL, json=payload)
    except:
        pass

def run_monitor():
    s = requests.Session()
    
    # 2. 登入 Zuvio
    login_url = "https://irs.zuvio.com.tw/b_irs/login/login_by_mail"
    login_data = {'email': EMAIL, 'password': PWD}
    s.post(login_url, data=login_data)
    
    # 3. 檢查點名狀態
    course_url = f"https://irs.zuvio.com.tw/student_v2/course/rollcall/{MY_COURSE_ID}"
    res = s.get(course_url)
    
    # 4. 判斷邏輯
    if "簽到" in res.text or "點名進行中" in res.text:
        # 發現點名，先通知 Discord
        send_dc(f"🚨 偵測到【{TARGET_NAME}】開啟點名！")
        
        # 延遲 20 秒（模擬人類操作）
        time.sleep(20)
        
        # 執行簽到
        check_in_url = f"https://irs.zuvio.com.tw/app_v2/check_in/{MY_COURSE_ID}"
        check_res = s.get(check_in_url)
        
        # 回傳簽到結果到 Discord
        send_dc(f"✅ 自動簽到執行完畢。回傳結果：{check_res.text[:100]}")
    else:
        # 沒在點名時，只在 GitHub 日誌紀錄，不吵 Discord
        print("目前沒有點名中")

if __name__ == "__main__":
    run_monitor()
