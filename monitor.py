import os
import requests
import re
import time

EMAIL = os.environ.get('ZUVIO_EMAIL')
PWD = os.environ.get('ZUVIO_PASSWORD')
WEBHOOK = os.environ.get('DISCORD_WEBHOOK')
TARGET_COURSE = "英語聽講(大學土木2乙)" 

def send_dc(msg):
    if WEBHOOK:
        requests.post(WEBHOOK, json={"content": msg})

def main():
    s = requests.Session()
    # 1. 嘗試登入
    login_url = "https://irs.zuvio.com.tw/irs/submitLogin"
    res = s.post(login_url, data={"email": EMAIL, "password": PWD, "remember_me": "1"})
    
    # 2. 印出登入後的最終網址
    print(f"登入後的網址：{res.url}")
    
    # 3. 檢查關鍵字
    if "login" in res.url:
        print("❌ 登入失敗：被踢回了登入頁面。可能是帳密錯誤或需要驗證碼。")
    else:
        print(f"✅ 登入後的網頁標題：{re.search('<title>(.*?)</title>', res.text).group(1)}")
    
    if not course_ids:
        print("❌ 無法從網頁取得任何課程。請檢查帳密是否正確，或帳號內是否有課程。")
        return

    print(f"✅ 成功進入系統，偵測到 {len(course_ids)} 門課程。")
    
    # 4. 逐一檢查這些課程
    for c_id in course_ids:
        # 獲取該課程的點名狀態頁面
        course_url = f"https://irs.zuvio.com.tw/student5/irs/rollcall/{c_id}"
        res = s.get(course_url)
        
        # 檢查網頁內容中是否有該課程名稱
        if TARGET_COURSE in res.text:
            print(f"🎯 鎖定目標課程 ID: {c_id}")
            
            # 檢查網頁內容是否顯示「點名進行中」
            # Zuvio 點名開啟時，網頁會出現簽到按鈕
            if "簽到" in res.text or "點名進行中" in res.text:
                send_dc(f"🚨 **偵測到【{TARGET_COURSE}】開啟點名！**")
                time.sleep(30)
                
                # 執行簽到 API
                checkin_url = f"https://irs.zuvio.com.tw/student5/ajax/checkin/{c_id}"
                checkin_res = s.post(checkin_url, data={"lat": 25.0, "lng": 121.5})
                
                if "success" in checkin_res.text or checkin_res.status_code == 200:
                    send_dc(f"✅ **【{TARGET_COURSE}】自動點名成功！**")
                else:
                    send_dc(f"❌ **【{TARGET_COURSE}】簽到失敗，回應：{checkin_res.text}**")
            else:
                print(f"😴 {TARGET_COURSE} 目前沒在點名。")
            break
    else:
        print(f"❓ 在課程清單中找不到「{TARGET_COURSE}」。")

if __name__ == "__main__":
    main()
