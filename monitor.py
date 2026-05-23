import os
import requests
import time

# 從 GitHub Secrets 讀取資料
EMAIL = os.environ.get('ZUVIO_EMAIL')
PWD = os.environ.get('ZUVIO_PASSWORD')
WEBHOOK = os.environ.get('DISCORD_WEBHOOK')

TARGET_COURSE = "英語聽講(大學土木2乙)" 

def send_dc(msg):
    if WEBHOOK:
        requests.post(WEBHOOK, json={"content": msg})

def main():
    s = requests.Session()
    # 模擬手機 App 的瀏覽器標頭，這最不容易被擋
    s.headers.update({
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1',
        'Referer': 'https://irs.zuvio.com.tw/',
        'Accept-Language': 'zh-TW,zh;q=0.9'
    })
    
    # 1. 嘗試登入 (換成更基礎的登入入口)
    login_url = "https://irs.zuvio.com.tw/irs/submitLogin"
    login_data = {
        "email": EMAIL,
        "password": PWD,
        "remember_me": "1"
    }
    
    # 先抓一次首頁取得基礎 Cookie
    s.get("https://irs.zuvio.com.tw/student5/irs/index")
    
    # 執行登入
    res = s.post(login_url, data=login_data)
    
    # 2. 驗證登入狀態 (直接去抓課程頁面，看網址有沒有被踢回登入頁)
    test_res = s.get("https://irs.zuvio.com.tw/student5/ajax/get_courses")
    
    if test_res.status_code != 200 or "courses" not in test_res.text:
        print("❌ 登入仍舊失敗。請確認：")
        print("1. Secrets 裡的帳號是否包含完整的學號或信箱")
        print("2. 密碼是否完全正確 (無空格)")
        # 顯示一點回傳內容方便 debug
        print(f"伺服器回傳狀態碼: {test_res.status_code}")
        return

    print("✅ 登入成功！正在掃描課程...")
    
    # 3. 處理課程資料
    data = test_res.json()
    found = False
    for course in data.get('courses', []):
        if TARGET_COURSE in course['name']:
            found = True
            print(f"🎯 鎖定課程：{course['name']}")
            
            if course.get('is_on_rollcall'):
                send_dc(f"🚨 **偵測到【{course['name']}】開啟點名！**\n系統將於 60 秒後自動簽到...")
                time.sleep(60)
                
                # 4. 執行簽到
                c_id = course['id']
                checkin_url = f"https://irs.zuvio.com.tw/student5/ajax/checkin/{c_id}"
                # 座標設為 0,0 或是隨便一個座標，通常一般點名不檢查這個，只要有傳資料就好
                checkin_res = s.post(checkin_url, data={"lat": 25.0, "lng": 121.5})
                
                if "success" in checkin_res.text or checkin_res.status_code == 200:
                    send_dc(f"✅ **【{course['name']}】自動點名成功！**")
                else:
                    send_dc(f"❌ **【{course['name']}】點名異常：{checkin_res.text}**")
            else:
                print(f"😴 {course['name']} 目前未開啟點名。")
    
    if not found:
        print(f"❓ 找不到名為「{TARGET_COURSE}」的課程。")

if __name__ == "__main__":
    main()
