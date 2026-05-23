import os
import requests
import re
import time

EMAIL = os.environ.get('ZUVIO_EMAIL')
PWD = os.environ.get('ZUVIO_PASSWORD')
WEBHOOK = os.environ.get('DISCORD_WEBHOOK')

# 只要名稱包含這段就會觸發
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
    
    # 2. 進入學生首頁
    res = s.get("https://irs.zuvio.com.tw/student5/irs/index")
    
    # --- 強化版 ID 抓取：嘗試三種不同的網頁特徵 ---
    ids = re.findall(r"course/(\d+)", res.text) + \
          re.findall(r"course\((\d+)\)", res.text) + \
          re.findall(r"student5/irs/rollcall/(\d+)", res.text)
    
    # 去除重複的 ID
    course_ids = list(set(ids))
    
    if not course_ids:
        print("❌ 依然找不到課程 ID。")
        # 偵錯：印出網頁有沒有出現任何課程關鍵字
        if "英語" in res.text: print("💡 提示：網頁裡有看到『英語』兩個字，但抓不到點名連結。")
        return

    print(f"✅ 成功！偵測到 {len(course_ids)} 門課程。")
    
    for c_id in course_ids:
        # 檢查該課程的名稱與點名狀態
        c_page = s.get(f"https://irs.zuvio.com.tw/student5/irs/rollcall/{c_id}")
        
        # 只要這門課的頁面有我們要的關鍵字
        if TARGET_COURSE in c_page.text:
            print(f"🎯 鎖定目標：ID {c_id}")
            
            if "簽到" in c_page.text or "點名進行中" in c_page.text:
                send_dc(f"🚨 **偵測到【{TARGET_COURSE}】開啟點名！**")
                time.sleep(10)
                # 簽到 API
                ck = s.post(f"https://irs.zuvio.com.tw/student5/ajax/checkin/{c_id}", data={"lat": 24.747, "lng": 121.745})
                if "success" in ck.text or ck.status_code == 200:
                    send_dc(f"✅ **【{TARGET_COURSE}】自動簽到成功！**")
                else:
                    send_dc(f"❌ 簽到失敗：{ck.text}")
            else:
                print(f"ℹ️ {TARGET_COURSE} 目前沒在點名。")
            return

    print(f"❓ 找不到包含「{TARGET_COURSE}」字樣的課程頁面。")

if __name__ == "__main__":
    main()
