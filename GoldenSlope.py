# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 21:54:47 2026

@author: Qing
"""

import requests, os, json, time
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
import GoldenSlope_signal as GSS


def get_data(token, data_id, start_date, end_date):
    '''交易資料'''
    data_url = 'https://api.finmindtrade.com/api/v4/data'
    data_params = {
        "dataset": "TaiwanStockPrice",
        "data_id": data_id,
        "start_date": start_date,
        "end_date": end_date,
        "token": token
    }
    data_headers = {'Authorization': 'Bearer ' + token }
    r = requests.get(data_url, headers = data_headers, params = data_params)
    print(f'get data: {data_id}, status:', r.status_code)
    if r.status_code == 200:
        data = r.json()
        # print(data)
        return data
    return None


def avg_data(data):
    '''均線資料'''
    if not data or "data" not in data or not data["data"]:
        return None
    df = pd.DataFrame(data["data"])
    # 檢查是否有 'close' 欄位
    if 'close' not in df.columns:
        return None
    # 1. 計算 5 日均線 (短期趨勢)
    df['MA5'] = df['close'].rolling(window=5).mean()
    # 2. 計算 20 日均線 (長期趨勢，通常稱為月線)
    df['MA20'] = df['close'].rolling(window=20).mean()
    # 季均線
    df['MA60'] = df['close'].rolling(window=60).mean()
    # MACDMomentumHybridStrategy 參數
    df['long_trend'] = df['close'].rolling(window=150).mean()
    df['roc'] = df['close'].pct_change(20)
    df['EMA12'] = df['close'].ewm(span=12, adjust=False).mean()
    df['EMA26'] = df['close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = df['EMA12'] - df['EMA26']
    df['MACD_signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['MACD_hist'] = df['MACD'] - df['MACD_signal']
    return df.dropna()


def load_portfolio(filepath="positions.json"):
    '''讀取 json 檔案'''
    # 預設結構
    default_data = {"position_list": []}

    # 1. 檔案不存在，或檔案長度為 0 (完全空白)
    if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
        return default_data

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            
            # 2. 確保讀出來是字典，且包含 position_list
            if isinstance(data, dict) and "position_list" in data:
                return data
            else:
                return default_data

    except json.JSONDecodeError:
        # 3. 萬一 JSON 格式被肉眼改壞或解析失敗，自動退回預設值
        print("⚠️ JSON 檔案解析失敗，使用預設空清單。")
        return default_data
    
def save_portfolio(data, filepath="positions.json"):
    """將持倉資料寫回 JSON 檔"""
    try:
        position_list = {"position_list": data}
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(position_list, f, ensure_ascii=False, indent=2)
        print("✅ 持倉資料已成功寫入 JSON。")
    except Exception as e:
        print(f"❌ 寫入 JSON 失敗: {e}")

def send_line_message(token, msg):
    '''發送 line 通知'''
    # 這裡填入你的 Line Channel Access Token 和 User ID
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + token
    }
    payload = {
        "to": "U1c0889ec2d8312c5825a113cef3bcc4d",
        "messages": [{"type": "text", "text": msg}]
    }
    requests.post(url, headers=headers, json=payload)



if __name__ == '__main__':
    # 1. 載入 .env 檔案
    load_dotenv()
    
    # 2. 現在 os.getenv 就能抓到檔案裡的內容了
    finmind_token = os.getenv('FINMIND_TOKEN')
    line_token = os.getenv('LINE_TOKEN')

    # 設定資料日期
    today = datetime.today()
    today_str = today.strftime('%Y-%m-%d')
    print('today:', today_str)
    start_date = today + timedelta(days = -400)
    start_date_str = start_date.strftime('%Y-%m-%d')
    print('start_date:', start_date_str)
    # 進行資料整理
    data_id_list = [
        '2330', '2454', '2308', '2317', '3711', '2383', '2303', '3037', '2891', '2345', 
        '2881', '2882', '2327', '1303', '3017', '2382', '2887', '2360', '2885', '2095',
        '6669', '3231', '2357', '2886', '2884', '2344', '2408', '2890', '2412', '2301', 
        '2883', '3008', '3443', '2880', '3653', '3665', '1216', '2892', '7769', '4958',
        '2368', '3661', '2395', '2449', '8046', '5880', '2603', '4904', '3045', '6505'
    ]
    stock_data_list = []
    for data_id in data_id_list:
        data = get_data(finmind_token, data_id, start_date_str, today_str)
        df = avg_data(data)
        if df is None:
            continue
        stock_data_list.append({'name': data_id, 'data': df})
        time.sleep(0.5)
    # 策略訊號
    position_data = load_portfolio()
    position_list = position_data['position_list']
    sell_list, buy_list, position_list = GSS.MACDMomentumHybridStrategy(stock_data_list, position_list)
    save_portfolio(position_list)
    action_result = []
    # 售出資料
    sell_result = '====== 賣出訊號 ====== \n'
    for sell_item in sell_list:
        sell_result += f"項目: {sell_item['name']} \n" \
                        f"最高價: {sell_item['highest_price']} \n" \
                        f"收盤價: {sell_item['close']} \n"
    action_result.append(sell_result)
    # 買入資料
    buy_result = '====== 買入訊號 ====== \n'
    for buy_item in buy_list:
        buy_result += f"項目: {buy_item['name']} \n" \
                        f"收盤價: {buy_item['close']} \n"
    action_result.append(buy_result)
    # 持有資料
    position_result = '====== 持有資料 ====== \n'
    for position_item in position_list:
        position_result += f"項目: {position_item['name']} \n" \
                        f"最高價: {position_item['highest_price']} \n" \
                        f"收盤價: {position_item['close']} \n"
    action_result.append(position_result)
    # 發送分析結果
    send_text = "\n\n".join(action_result)
    send_line_message(line_token, send_text)




