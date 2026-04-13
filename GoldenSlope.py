# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 21:54:47 2026

@author: Qing
"""

import requests, os
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv

def get_data(token, data_id, start_date, end_date):
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
    print(r.status_code)
    if r.status_code == 200:
        data = r.json()
        # print(data)
        return data
    return None

def cross_data(data):
    df = pd.DataFrame(data["data"])
    # 1. 計算 5 日均線 (短期趨勢)
    df['MA5'] = df['close'].rolling(window=5).mean()
    # 2. 計算 20 日均線 (長期趨勢，通常稱為月線)
    df['MA20'] = df['close'].rolling(window=20).mean()
    # 黃金交叉
    df['greater'] = df['MA5'] > df['MA20']
    # 判斷「交叉點」：今天的大於(True) 且 昨天的大於(False)
    # .shift(1) 的意思是把數據「往下移一格」，也就是抓取昨天的狀態
    df['golden_cross'] = (df['greater'] == True) & (df['greater'].shift(1) == False)
    # 1. 死亡交叉
    df['less'] = df['MA5'] < df['MA20']
    # 2. 判斷「死亡交叉點」：今天的小於(True) 且 昨天的小於(False)
    # 也就是昨天 MA5 >= MA20，今天卻變成了 MA5 < MA20
    df['death_cross'] = (df['less'] == True) & (df['less'].shift(1) == False)
    # 計算 MA20 的斜率（今天跟昨天的差值）
    df['MA20_slope'] = df['MA20'] - df['MA20'].shift(1)
    # 計算 5 日平均成交量 (均量)
    df['VMA5'] = df['Trading_Volume'].rolling(5).mean()
    
    return df

def buy_signal(token, data_id, input_df):
    df = input_df.copy()
    today = df.iloc[-1]
    yestoday = df.iloc[-2]
    msg = 'nothing to do'
    if today['death_cross']:
        msg = f"🔴【賣出訊號】{data_id}\n" \
              f"昨日日均線：{yestoday['MA5']}\n" \
              f"昨日月均線：{yestoday['MA20']}\n" \
              f"日均線：{today['MA5']}\n" \
              f"月均線：{today['MA20']}\n" \
              f"今日收盤：{today['close']}\n" \
              f"💡 動作：趨勢轉弱，明日開盤出清。"
    elif today['golden_cross'] and today['MA20_slope'] > 0:
        msg = f"🟢【買進訊號】{data_id}\n" \
              f"昨日日均線：{yestoday['MA5']}\n" \
              f"昨日月均線：{yestoday['MA20']}\n" \
              f"日均線：{today['MA5']}\n" \
              f"月均線：{today['MA20']}\n" \
              f"今日收盤：{today['close']}\n" \
              f"斜率：{today['MA20_slope']}\n" \
              f"成交量：{today['Trading_Volume']}\n" \
              f"💡 動作：晚上設定預約單，明日開盤買入。"
    else:
        msg = f"[不動作] {data_id}\n" \
              f"昨日日均線：{yestoday['MA5']}\n" \
              f"昨日月均線：{yestoday['MA20']}\n" \
              f"日均線：{today['MA5']}\n" \
              f"月均線：{today['MA20']}\n" \
              f"今日收盤：{today['close']}\n" \
              f"斜率：{today['MA20_slope']}\n" \
              f"成交量：{today['Trading_Volume']}"
    send_line_message(token, msg)
    

def send_line_message(token, msg):
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
    start_date = today + timedelta(days = -60)
    start_date_str = start_date.strftime('%Y-%m-%d')
    print('start_date:', start_date_str)
    # 進行資料篩選
    data_id = '2330'
    data = get_data(finmind_token, data_id, start_date_str, today_str)
    df = cross_data(data)
    buy_signal(line_token, data_id, df)




