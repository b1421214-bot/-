import os
import requests
import time

# 從 GitHub Secrets 讀取資料
EMAIL = os.environ.get('ZUVIO_EMAIL')
PWD = os.environ.get('ZUVIO_PASSWORD')
WEBHOOK = os.environ.get('DISCORD_WEBHOOK')

# 設定目標課程關鍵字
TARGET_COURSE = "英語聽講(大學土木2乙)" 

def send_dc(msg):
    if WEBHOOK:
        requests.post(WEBHOOK, json={"content": msg})

def main():
    s = requests.Session()
    
    # 1. 登入 Zuvio
    login_url = "https://irs.zuvio.com.tw/irs/submitLogin"
    login_data = {"email": EMAIL, "password": PWD}
    res = s.post(login_url, data=login_data)
    
    if "登入失敗" in res.text:
        print("登入失敗，請檢查帳號密碼。")
        return

    # 2. 獲取課程清單
    try:
        course_res = s.get("https://irs.zuvio.com.tw/student5/ajax/get_courses").json()
    except:
        print("無法取得課程列表")
        return
    
    for course in course_res.get('courses', []):
        # 搜尋指定的課程名稱
        if TARGET_COURSE in course['name']:
            print(f"正在檢查課程：{course['name']}")
            
            # 3. 檢查是否正在點名 (is_on_rollcall)
            if course.get('is_on_rollcall'):
                send_dc(f"🚨 **偵測到【{course['name']}】開啟點名！**\n系統將於 60 秒後執行自動簽到...")
                
                # 模擬真人等待
                time.sleep(60)
                
                # 4. 執行簽到
                # 一般點名不需要代碼，直接對該課程 ID 發送簽到請求
                course_id = course['id']
                rollcall_url = f"https://irs.zuvio.com.tw/student5/ajax/checkin/{course_id}"
                
                # 傳送預設座標 (校園附近) 避免 GPS 檢查
                checkin_data = {"lat": 25.0, "lng": 121.5}
                checkin_res = s.post(rollcall_url, data=checkin_data)
                
                if checkin_res.status_code == 200:
                    send_dc(f"✅ **【{course['name']}】自動點名成功！**")
                else:
                    send_dc(f"❌ **【{course['name']}】點名失敗，狀態碼：{checkin_res.status_code}**")
            else:
                print(f"課程 {course['name']} 目前未點名。")

if __name__ == "__main__":
    main()
