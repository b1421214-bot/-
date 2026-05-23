import os
import requests
import time

EMAIL = os.environ.get('ZUVIO_EMAIL')
PWD = os.environ.get('ZUVIO_PASSWORD')
WEBHOOK = os.environ.get('DISCORD_WEBHOOK')
TARGET_COURSE = "英語聽講" 

def send_dc(msg):
    if WEBHOOK:
        try: requests.post(WEBHOOK, json={"content": msg})
        except: pass

def main():
    s = requests.Session()
    s.headers.update({'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1'})
    
    # 1. 登入
    s.post("https://irs.zuvio.com.tw/irs/submitLogin", data={"email": EMAIL, "password": PWD, "remember_me": "1"})
    
    # 2. 核心：直接向 Zuvio API 請求課程清單 (不管 student3 還是 student5 都試一遍)
    courses = []
    for ver in ["student5", "student3"]:
        try:
            api_url = f"https://irs.zuvio.com.tw/{ver}/ajax/get_courses"
            res = s.get(api_url)
            if res.status_code == 200 and "courses" in res.text:
                courses = res.json().get('courses', [])
                if courses:
                    print(f"✅ 成功透過 {ver} 取得課程清單！")
                    break
        except:
            continue

    if not courses:
        print("❌ 登入成功但 API 未回傳課程。")
        return

    print(f"📊 偵測到 {len(courses)} 門課程。")
    
    # 3. 掃描目標課程
    for c in courses:
        c_name = c.get('name', '')
        c_id = c.get('id')
        
        if TARGET_COURSE in c_name:
            print(f"🎯 鎖定：{c_name} (ID: {c_id})")
            
            # 檢查點名狀態
            # 有些版本點名資訊就在 API 裡 (is_on_rollcall)
            is_on = c.get('is_on_rollcall')
            
            # 保險起見，去檢查一下點名網頁內容
            roll_page = s.get(f"https://irs.zuvio.com.tw/student5/irs/rollcall/{c_id}")
            
            if is_on or "簽到" in roll_page.text or "點名進行中" in roll_page.text:
                send_dc(f"🚨 **偵測到【{c_name}】開啟點名！**")
                time.sleep(10)
                # 執行簽到
                ck = s.post(f"https://irs.zuvio.com.tw/student5/ajax/checkin/{c_id}", data={"lat": 24.747, "lng": 121.745})
                if "success" in ck.text:
                    send_dc(f"✅ **【{c_name}】自動簽到成功！**")
                else:
                    send_dc(f"⚠️ 嘗試簽到，回應：{ck.text}")
            else:
                print(f"ℹ️ {c_name} 目前沒有點名。")
            return

    print(f"❓ 找不到包含「{TARGET_COURSE}」的課程。")

if __name__ == "__main__":
    main()
