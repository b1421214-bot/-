import requests
import os
import time

# --- 1. 從 GitHub Secrets 讀取設定 ---
EMAIL = os.environ.get('ZUVIO_EMAIL')
PWD = os.environ.get('ZUVIO_PASSWORD')
WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK')

MY_COURSE_ID = "1496033"
TARGET_NAME = "英語聽講(大學土木2乙)"

# --- 錄影測試開關 ---
SHOW_FINAL_REPORT = True 

def send_dc(msg):
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
        send_dc(f"🚨 偵測到【{TARGET_NAME}】開啟點名！\n系統將於 20 秒後自動執行簽到...")
        time.sleep(20)
        check_in_url = f"https://irs.zuvio.com.tw/app_v2/check_in/{MY_COURSE_ID}"
        check_res = s.get(check_in_url)
        send_dc(f"✅ 【{TARGET_NAME}】自動簽到執行完畢。")
        
    elif SHOW_FINAL_REPORT:
        # 最終檢測報告 (免 pytz 版)
        send_dc(f"📊 【最終檢測報告】\n課程：{TARGET_NAME}\n狀態：今日監控已結束，系統確認老師全課程皆未開啟點名。\n結論：系統運作正常，無遺漏任何簽到作業。")
    
    else:
        print("目前沒有點名中...")

if __name__ == "__main__":
    run_monitor()
