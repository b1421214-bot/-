import os
import requests
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
    s.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'})
    
    # 1. 登入
    login_url = "https://irs.zuvio.com.tw/irs/submitLogin"
    res = s.post(login_url, data={"email": EMAIL, "password": PWD, "remember_me": "1"})
    
    # 2. 嘗試尋找正確的課程 API 路徑 (多版本偵測)
    # 這裡列出 Zuvio 常見的三個版本路徑
    api_paths = [
        "https://irs.zuvio.com.tw/student5/ajax/get_courses",
        "https://irs.zuvio.com.tw/student3/ajax/get_courses",
        "https://irs.zuvio.com.tw/zuvio/ajax/get_courses"
    ]
    
    data = None
    active_url = ""
    
    for url in api_paths:
        test_res = s.get(url)
        if test_res.status_code == 200 and "courses" in test_res.text:
            data = test_res.json()
            active_url = url.replace("ajax/get_courses", "") # 取得基礎路徑 (如 student5/ 或 student3/)
            print(f"✅ 成功找到 API 路徑: {url}")
            break
    
    if not data:
        print("❌ 登入成功但找不到課程清單。")
        print(f"最後一次嘗試的狀態碼: {test_res.status_code}")
        return

    # 3. 掃描課程
    found = False
    for course in data.get('courses', []):
        if TARGET_COURSE in course['name']:
            found = True
            print(f"🎯 鎖定課程：{course['name']}")
            
            if course.get('is_on_rollcall'):
                send_dc(f"🚨 **偵測到【{course['name']}】開啟點名！**")
                time.sleep(30) # 縮短等待時間
                
                # 4. 簽到 (動態路徑)
                c_id = course['id']
                checkin_url = f"{active_url}ajax/checkin/{c_id}"
                checkin_res = s.post(checkin_url, data={"lat": 25.0, "lng": 121.5})
                
                if "success" in checkin_res.text or checkin_res.status_code == 200:
                    send_dc(f"✅ **【{course['name']}】自動點名成功！**")
                else:
                    send_dc(f"❌ **【{course['name']}】點名異常：{checkin_res.text}**")
            else:
                print(f"ℹ️ {course['name']} 目前未開啟點名。")
    
    if not found:
        print(f"❓ 找不到名為「{TARGET_COURSE}」的課程。")
        # 印出所有找到的課名，方便你核對
        print("目前帳號內的課程有：", [c['name'] for c in data.get('courses', [])])

if __name__ == "__main__":
    main()
