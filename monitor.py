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
    session = requests.Session()
    
    # 1. 登入 Zuvio
    login_url = "https://irs.zuvio.com.tw/irs/submitLogin"
    login_data = {'email': ZUVIO_EMAIL, 'password': ZUVIO_PASSWORD}
    
    try:
        res = session.post(login_url, data=login_data)
        if "登入失敗" in res.text:
            print("❌ Zuvio 登入失敗，請檢查帳密。")
            return
    except:
        print("❌ 網路連線異常")
        return

    # 2. 抓取課程列表
    try:
        # 取得學生首頁
        course_res = session.get("https://irs.zuvio.com.tw/course/list")
        # 這裡用最簡單的方式找出所有課程 ID (IRS ID)
        import re
        course_ids = re.findall(r'https://irs.zuvio.com.tw/student/course/(\[0-9\]+)', course_res.text)
        # 去重
        course_ids = list(set(course_ids))
    except:
        print("❌ 無法獲取課程列表")
        return

    current_time = datetime.now().strftime("%H:%M")
    print(f"✅ 登入成功 | 檢查時間: {current_time} | 找到 {len(course_ids)} 門課程")

    # 3. 逐一檢查課程是否有「點名」
    found_any = False
    for c_id in course_ids:
        try:
            # 進入點名頁面檢查
            checkin_url = f"https://irs.zuvio.com.tw/student/course/{c_id}/checkin"
            checkin_res = session.get(checkin_url)
            
            # 判斷網頁內容是否有「限時簽到」或「簽到中」等字眼 (視 Zuvio 網頁結構而定)
            # 這裡用最常見的關鍵字判斷
            if "簽到" in checkin_res.text and "目前不在簽到時間" not in checkin_res.text:
                msg = f"🚀 【Zuvio 偵測到點名！】\n課程 ID：{c_id}\n時間：{current_time}\n請盡快登入簽到！"
                send_discord(msg)
                print(f"🔔 發現點名！ID: {c_id}")
                found_any = True
        except:
            continue

    if not found_any:
        print("😴 目前所有課程都沒有點名活動。")

if __name__ == "__main__":
    run_check()
