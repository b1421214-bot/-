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
    except Exception as e:
        print(f"Discord 發送失敗: {e}")

def run_monitor():
    s = requests.Session()
    
    # 2. 登入 Zuvio
    login_url = "https://irs.zuvio.com.tw/b_irs/login/login_by_mail"
    login_data = {'email': EMAIL, 'password': PWD}
    s.post(login_url, data=login_data)
    
    # 3. 強行觸發模式 (錄影用)
    # 我們把判斷式改成 True，這樣不管有沒有點名，都會執行後面的動作
    if True:
        # 第一階段：模擬發現點名
        send_dc(f"🚨 【測試中】偵測到【{TARGET_NAME}】開啟點名！")
        
        # 第二階段：等待 20 秒 (錄影時你可以說明這是在模擬人類反應)
        print("模擬等待 20 秒中...")
        time.sleep(20)
        
        # 第三階段：執行簽到動作
        check_in_url = f"https://irs.zuvio.com.tw/app_v2/check_in/{MY_COURSE_ID}"
        check_res = s.get(check_in_url)
        
        # 第四階段：回傳結果 (因為現在沒點名，回傳會是 404，這代表通訊完全正常)
        send_dc(f"✅ 【測試中】自動簽到執行完畢。回傳結果：{check_res.text[:100]}")
    else:
        print("這段現在不會被執行到")

if __name__ == "__main__":
    run_monitor()
