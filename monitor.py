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
        try:
            requests.post(WEBHOOK, json={"content": msg})
        except:
            print("Discord 發送失敗")

def main():
    s = requests.Session()
    # 增加瀏覽器標頭，讓 Zuvio 以為我們是真人
    s.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    })
    
    # 1. 執行登入
    login_url = "https://irs.zuvio.com.tw/irs/submitLogin"
    login_data = {
        "email": EMAIL,
        "password": PWD,
        "remember_me": "1"
    }
    login_res = s.post(login_url, data=login_data)
    
    # 檢查是否登入成功 (透過網頁內容判斷)
    if "學生" not in login_res.text and "首頁" not in login_res.text:
        print("❌ 登入失敗，請確認帳號密碼是否正確")
        # --- 加入下面這行 ---
        print(f"偵錯訊息：網頁回傳內容前100字：{login_res.text[:100]}")
        # ------------------
        return

    # 2. 直接訪問學生首頁確保 Session 建立
    s.get("https://irs.zuvio.com.tw/student5/irs/index")

    # 3. 獲取課程清單 (改用另一個更穩定的 API)
    course_api = "https://irs.zuvio.com.tw/student5/ajax/get_courses"
    try:
        res = s.get(course_api)
        data = res.json()
        
        if 'courses' not in data:
            print(f"❌ 找不到課程欄位，伺服器回應：{res.text}")
            return
            
        courses = data['courses']
        found = False
        
        for course in courses:
            if TARGET_COURSE in course['name']:
                found = True
                print(f"✅ 找到課程：{course['name']}")
                
                # 檢查是否點名
                if course.get('is_on_rollcall'):
                    send_dc(f"🚨 **偵測到【{course['name']}】開啟點名！**\n1分鐘後自動簽到...")
                    time.sleep(60)
                    
                    # 4. 執行簽到
                    c_id = course['id']
                    checkin_url = f"https://irs.zuvio.com.tw/student5/ajax/checkin/{c_id}"
                    # 模擬座標 (可視情況修改為學校座標)
                    checkin_res = s.post(checkin_url, data={"lat": 25.0, "lng": 121.5})
                    
                    if "success" in checkin_res.text or checkin_res.status_code == 200:
                        send_dc(f"✅ **【{course['name']}】自動點名成功！**")
                    else:
                        send_dc(f"❌ **【{course['name']}】點名回報異常：{checkin_res.text}**")
                else:
                    print(f"ℹ️ {course['name']} 目前沒有點名。")
        
        if not found:
            print(f"❓ 登入成功，但在課程清單中沒看到「{TARGET_COURSE}」")
            print("請檢查課程名稱是否完全正確，或嘗試縮短關鍵字（例如只用：英語聽講）")

    except Exception as e:
        print(f"💥 發生錯誤：{str(e)}")

if __name__ == "__main__":
    main()
