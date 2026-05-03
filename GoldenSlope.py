# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 21:54:47 2026

@author: Qing
"""

import requests, os
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
    print(r.status_code)
    if r.status_code == 200:
        data = r.json()
        # print(data)
        return data
    return None


def avg_data(data):
    '''均線資料'''
    df = pd.DataFrame(data["data"])
    # 1. 計算 5 日均線 (短期趨勢)
    df['MA5'] = df['close'].rolling(window=5).mean()
    # 2. 計算 20 日均線 (長期趨勢，通常稱為月線)
    df['MA20'] = df['close'].rolling(window=20).mean()
    # 計算 MA20 的斜率（今天跟昨天的差值）
    df['MA20_slope'] = df['MA20'] - df['MA20'].shift(1)
    # 計算 5 日平均成交量 (均量)
    df['VMA5'] = df['Trading_Volume'].rolling(5).mean()
    return df


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
    start_date = today + timedelta(days = -60)
    start_date_str = start_date.strftime('%Y-%m-%d')
    print('start_date:', start_date_str)
    # 進行資料整理
    data_id = '2330'
    data = get_data(finmind_token, data_id, start_date_str, today_str)
    df = avg_data(data)
    # 分析數據
    cross_signal = GSS.golden_cross_signal(data_id, df)
    mean_reversion_signal = GSS.strategy_mean_reversion(data_id, df)
    trend_following_signal = GSS.strategy_trend_following(data_id, df)
    # 發送分析結果
    msg = []
    msg.append(cross_signal)
    msg.append(mean_reversion_signal)
    msg.append(trend_following_signal)
    final_text = "\n".join(msg)
    send_line_message(line_token, final_text)




