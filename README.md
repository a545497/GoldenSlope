📈 GoldenSlope: Zen Trading Strategy & Automation

![Monitor Status](https://github.com/a545497/GoldenSlope/actions/workflows/daily_check.yml/badge.svg)
[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

"In the market's noise, find the path of least resistance."
GoldenSlope 是一個專為「佛系投資人」設計的自動化監控系統，結合了經典的均線交叉理論與斜率動能過濾。


📖 核心理念：為何選擇 GoldenSlope？

市場上充滿了各種指標，但 GoldenSlope 專注於最純粹的「趨勢確認」。
我們不追求頻繁交易，而是透過雙重確認機制來捕捉高勝率的波段：

1. 黃金交叉 (Golden Cross)：確認短期趨勢突破。

2. 斜率動能 (Slope Filter)：確保長期趨勢 (MA20) 具有足夠的支撐動力。

3. 順勢波段策略 (Trend Following) —— 「追蹤強勢趨勢」:確保在多頭行情中「抱緊處理」，吃滿整段主升段。

4. 逆勢回歸策略 (Mean Reversion) —— 「捕捉超跌反彈」:在市場恐慌、股價嚴重低於平均成本時識別「超跌點」，實現低位佈局。


🛠️ 技術架構 (Technical Stack)

。Language: Python 3.9+

。Data Source: FinMind API (Taiwan Stock Market)

。Analysis: Pandas (Vectorized calculation)

。Automation: GitHub Actions (Cron Job)

。Notification: Line Messaging API (Line Notify)

。Security: GitHub Secrets & python-dotenv


🚀 快速開始 (Quick Start)

1. 本地環境建置
# 複製專案
git clone https://github.com/a545497/GoldenSlope.git

cd GoldenSlope

# 安裝依賴套件
pip install -r requirements.txt

設定環境變數

在專案根目錄建立 .env 檔案並填入憑證：

FINMIND_TOKEN=your_finmind_api_token

LINE_TOKEN=your_line_notify_token

執行監控

python GoldenSlope.py


🤖 自動化部署 (CI/CD)

本專案利用 GitHub Actions 實現每日自動化監控。

。執行時間：每週一至週五 台灣時間 15:00 (UTC 07:00)。

。自動通知：當策略觸發「買進」或「賣出」訊號時，系統將自動推送詳細報告至您的 Line。


📜 免責聲明 (Disclaimer)

本專案僅供技術研究與程式開發學習之用，不構成任何投資建議。投資有風險，入市需謹慎。

💡

如果您對本專案感興趣，歡迎 Star 收藏或提出 Issue 交流！