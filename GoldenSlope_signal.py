# -*- coding: utf-8 -*-
"""
Created on Sun May  3 21:50:39 2026

@author: user
"""


def golden_cross_signal(data_id, input_df):
    '''黃金交叉量化分析'''
    df = input_df.copy()
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
    today = df.iloc[-1]
    msg = 'nothing to do'
    if today['death_cross']:
        msg = f"==== 交叉量化分析 ====\n" \
              f"🔴【賣出訊號】{data_id}\n" \
              f"💡 動作：趨勢轉弱，明日開盤出清。\n"
    elif today['golden_cross'] and today['MA20_slope'] > 0:
        msg = f"==== 交叉量化分析 ====\n" \
              f"🟢【買進訊號】{data_id}\n" \
              f"💡 動作：晚上設定預約單，明日開盤買入。\n"
    else:
        msg = f"==== 交叉量化分析 ====\n" \
              f"[不動作] {data_id}\n" \
              f"成交量：{today['Trading_Volume']}\n"
    return msg


def strategy_trend_following(data_id, input_df):
    '''順勢追隨分析'''
    df = input_df.copy()
    # 1. 定義買入與賣出訊號
    df['entry_sig'] = (df['close'] > df['MA20']) & (df['bias_ratio'] < 1.03)
    df['exit_sig'] = (df['close'] < df['MA20'])
    today = df.iloc[-1]
    msg = 'nothing to do'
    if today['exit_sig']:
        msg = f"==== 順勢追隨分析 ====\n" \
              f"🔴【賣出訊號】{data_id}\n" \
              f"💡 動作：趨勢轉弱，明日開盤出清。\n"
    elif today['entry_sig']:
        msg = f"==== 順勢追隨分析 ====\n" \
              f"🟢【買進(持有)訊號】{data_id}\n" \
              f"💡 動作：晚上設定預約單，明日開盤買入。\n"
    else:
        msg = f"==== 順勢追隨分析 ====\n" \
              f"[不動作] {data_id}\n"
    return msg


def strategy_mean_reversion(data_id, input_df):
    '''逆勢均線回歸分析'''
    df = input_df.copy()
    # 1. 定義買入與賣出訊號
    df['entry_sig'] = (df['close'] < df['MA20']) & (df['bias_ratio'] < 0.92)
    df['exit_sig'] = (df['close'] > df['MA20']) & (df['bias_ratio'] > 1.05)
    today = df.iloc[-1]
    msg = 'nothing to do'
    if today['exit_sig']:
        msg = f"==== 逆勢均線回歸分析 ====\n" \
              f"🔴【賣出訊號】{data_id}\n" \
              f"💡 動作：趨勢轉弱，明日開盤出清。\n"
    elif today['entry_sig']:
        msg = f"==== 逆勢均線回歸分析 ====\n" \
              f"🟢【買進(持有)訊號】{data_id}\n" \
              f"💡 動作：晚上設定預約單，明日開盤買入。\n"
    else:
        msg = f"==== 逆勢均線回歸分析 ====\n" \
              f"[不動作] {data_id}\n" 
    return msg


