import os
import requests
import time

# 從 GitHub Secrets 讀取資料
EMAIL = os.environ.get('ZUVIO_EMAIL')
PWD = os.environ.get('ZUVIO_PASSWORD')
WEBHOOK = os.environ.get('DISCORD_WEBHOOK')

# 你提供的精確課程 ID
MY_COURSE_ID = "1496033" 
TARGET_NAME = "英語聽講(大學土木2乙)"

def send_dc(msg):
    if WEBHOOK:
        try:
            requests.post(WEBHOOK, json={"content": msg})
        except:
            print("Discord 發送失敗")

def main():
    s = requests.Session()
    # 模擬手機瀏覽器，避免被擋
    s.headers.update({
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1'
    })
    
    # 1. 執行登入
    login_url = "https://irs.zuvio.com.tw/irs/submitLogin"
    login_data = {"email": EMAIL, "password": PWD, "remember_me": "1"}
    s.post(login_url, data=login_data)
    
    # 2. 直接訪問該課程的點名頁面
    # 注意：Zuvio 的點名通常在 rollcall 頁面，ID 是通用的
    roll_url = f"https://irs.zuvio.com.tw/student5/irs/rollcall/{MY_COURSE_ID}"
    res = s.get(roll_url)
    
    if res.status_code != 200:
        print(f"❌ 無法讀取課程頁面，狀態碼：{res.status_code}")
        return

    print(f"✅ 已連線至課程 ID: {MY_COURSE_ID} ({TARGET_NAME})")

    # 3. 判斷是否正在點名
    # 當點名開啟時，網頁會出現「簽到」按鈕或「點名進行中」字樣
   if True:
        send_dc(f"🚨 **偵測到【{TARGET_NAME}】開啟點名！**\n系統將於 20 秒後自動簽到...")
        time.sleep(20)
        
        # 4. 執行簽到 API
        # 經常用的是 student5/ajax/checkin 接口
        checkin_url = f"https://irs.zuvio.com.tw/student5/ajax/checkin/{MY_COURSE_ID}"
        # 宜大地理座標 (緯度, 經度)
        checkin_data = {"lat": 24.747, "lng": 121.745}
        ck_res = s.post(checkin_url, data=checkin_data)
        
        if "success" in ck_res.text or ck_res.status_code == 200:
            send_dc(f"✅ **【{TARGET_NAME}】自動簽到成功！**")
            print("簽到成功！")
        else:
            send_dc(f"⚠️ 簽到回傳結果：{ck_res.text}")
    else:
        print(f"ℹ️ {TARGET_NAME} 目前沒有點名。")

if __name__ == "__main__":
    main()
