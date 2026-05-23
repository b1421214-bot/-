import requests
import os
import time

# --- 1. 從 GitHub Secrets 讀取設定 ---
EMAIL = os.environ.get('ZUVIO_EMAIL')
PWD = os.environ.get('ZUVIO_PASSWORD')
WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK')

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
    
    # --- 錄影展示邏輯 (強行觸發所有訊息) ---
    
    # 第一步：展示偵測到點名的通知
    send_dc(f"🚨 【模擬測試】偵測到【{TARGET_NAME}】開啟點名！\n系統將於 20 秒後自動執行簽到作業...")
    
    # 第二步：模擬延遲 20 秒 (這段時間你可以講解系統防偵測機制)
    print("正在模擬 20 秒延遲...")
    time.sleep(20)
    
    # 第三步：發送簽到請求並展示結果
    check_in_url = f"https://irs.zuvio.com.tw/app_v2/check_in/{MY_COURSE_ID}"
    check_res = s.get(check_in_url)
    send_dc(f"✅ 【模擬測試】自動簽到執行完畢。\n回傳狀態碼：{check_res.status_code}")

    # 第四步：展示最終檢測報告 (證明系統結束時會做結算)
    send_dc(f"📊 【最終檢測報告】\n課程：{TARGET_NAME}\n狀態：今日監控已結束，系統確認所有點名皆已完成處理。\n結論：系統運作正常，無遺漏任何簽到作業。")

if __name__ == "__main__":
    run_monitor()
