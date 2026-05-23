import os
import requests
import re
import time

# 從 GitHub Secrets 讀取資料
EMAIL = os.environ.get('ZUVIO_EMAIL')
PWD = os.environ.get('ZUVIO_PASSWORD')
WEBHOOK = os.environ.get('DISCORD_WEBHOOK')

# 目標課程名稱
TARGET_COURSE = "英語聽講(大學土木2乙)" 

def send_dc(msg):
    if WEBHOOK:
        try:
            requests.post(WEBHOOK, json={"content": msg})
        except:
            print("Discord 發送失敗")

def main():
    s = requests.Session()
    s.headers.update({
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1'
    })
    
    # 1. 執行登入
    login_url = "https://irs.zuvio.com.tw/irs/submitLogin"
    login_data = {"email": EMAIL, "password": PWD, "remember_me": "1"}
    s.post(login_url, data=login_data)
    
    # 2. 獲取課程主頁
    index_page = s.get("https://irs.zuvio.com.tw/student5/irs/index")
    
    # 3. 找出所有課程 ID
    course_ids = re.findall(r"course\((\d+)\)", index_page.text)
    
    if not course_ids:
        print("❌ 登入成功但無法取得課程列表。")
        return

    print(f"✅ 成功進入系統，偵測到 {len(course_ids)} 門課程。")
    found_target = False

    # 4. 檢查每一門課
    for c_id in course_ids:
        # 訪問點名頁面
        rollcall_url = f"https://irs.zuvio.com.tw/student5/irs/rollcall/{c_id}"
        res = s.get(rollcall_url)
        
        # 判斷是否為目標課程
        if TARGET_COURSE in res.text:
            found_target = True
            print(f"🎯 找到目標課程：{TARGET_COURSE}")
            
            # 檢查是否有點名按鈕或正在點名的字樣
            if "簽到" in res.text or "點名進行中" in res.text:
                send_dc(f"🚨 **偵測到【{TARGET_COURSE}】開啟點名！**\n系統將於 30 秒後自動簽到...")
                time.sleep(30)
                
                # 執行簽到 API
                checkin_url = f"https://irs.zuvio.com.tw/student5/ajax/checkin/{c_id}"
                # 傳送基本座標
                checkin_res = s.post(checkin_url, data={"lat": 24.747, "lng": 121.745}) # 宜大約略座標
                
                if "success" in checkin_res.text or checkin_res.status_code == 200:
                    send_dc(f"✅ **【{TARGET_COURSE}】自動點名成功！**")
                    print("點名成功！")
                else:
                    send_dc(f"❌ **【{TARGET_COURSE}】簽到失敗：{checkin_res.text}**")
            else:
                print(f"ℹ️ {TARGET_COURSE} 目前沒在點名。")
            break
            
    if not found_target:
        print(f"❓ 在課程清單中沒看到「{TARGET_COURSE}」")

if __name__ == "__main__":
    main()
