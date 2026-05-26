import requests
import os
from datetime import datetime

# 從 GitHub Secrets 讀取資訊
ZUVIO_EMAIL = os.environ.get('ZUVIO_EMAIL')
ZUVIO_PASSWORD = os.environ.get('ZUVIO_PASSWORD')
DISCORD_WEBHOOK = os.environ.get('DISCORD_WEBHOOK')

def send_discord(msg):
    if DISCORD_WEBHOOK:
        try:
            requests.post(DISCORD_WEBHOOK, json={"content": msg}, timeout=10)
        except Exception as e:
            print(f"Discord 發送失敗: {e}")

def run_check():
    # 這裡放你原本的 Zuvio 登入與抓取邏輯
    # ... (請保留你原本登入並取得 course_list 的程式碼) ...
    
    # 範例邏輯：
    current_time = datetime.now().strftime("%H:%M")
    print(f"目前檢查時間: {current_time}")

    # 修改後的邏輯：只要在課程時間內，發現有點名就發通知
    # 這裡可以根據你之前的需求，微調時間判斷
    for course in course_list:
        if course.get('has_checkin'):
            msg = f"🚀 【Zuvio 偵測到點名！】\n課程：{course['name']}\n時間：{current_time}"
            send_discord(msg)
            print("已發送點名通知")
            return # 抓到一個就結束，避免洗板

# 執行
if __name__ == "__main__":
    try:
        run_check()
    except Exception as e:
        print(f"執行發生錯誤: {e}")
