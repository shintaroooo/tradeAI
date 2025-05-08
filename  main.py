# main.py

import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd

from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# OpenAI APIキーの設定
import os
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")  # 環境変数で管理推奨

# Streamlit UI
st.title("💹 テクニカルトレード戦略AI")
st.markdown("FX初心者向けに、テクニカル分析から戦略を自動提案します。")

# 入力項目
symbol = st.text_input("銘柄コードを入力（例：USDJPY=X, EURUSD=X, AAPLなど）", value="USDJPY=X")
start_date = st.date_input("分析開始日", pd.to_datetime(datetime(2023, 1, 1)))
end_date = st.date_input("分析終了日", pd.to_datetime(datetime.today()))

# 実行トリガー
if st.button("分析を開始する"):
    with st.spinner("データ取得中..."):
        data = yf.download(symbol, start=start_date, end=end_date)

    if data.empty:
        st.error("データが取得できませんでした。銘柄コードを確認してください。")
    else:
        st.success("データ取得完了 ✅")

        # 簡易テクニカル指標の算出
        data['SMA_14'] = data['Close'].rolling(window=14).mean()
        data['RSI'] = 100 - (100 / (1 + (data['Close'].diff().clip(lower=0).rolling(14).mean() /
                                        data['Close'].diff().clip(upper=0).abs().rolling(14).mean())))
        
        # 最新値を抽出
        latest_close = data['Close'].iloc[-1]
        latest_rsi = data['RSI'].iloc[-1]

        # LangChainによるプロンプト生成
        template = PromptTemplate.from_template("""
あなたはFX初心者向けのテクニカルトレード戦略アドバイザーです。
次のテクニカル分析の数値を参考に、今後1週間の予想・戦略を提供してください。

- 銘柄: {symbol}
- 期間: {start_date} 〜 {end_date}
- 現在価格: {latest_close}
- RSI: {latest_rsi}

必要な出力:
1. テクニカル分析結果
2. 勝率の高いエントリータイミング
3. ロング/ショートエントリ戦略
4. 損切り・利確ライン
5. 初心者への心構え
6. 簡易バックテストの評価（例：勝率、リスクリワード比）

出力は見やすく箇条書きで。
""")

        prompt = template.format(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            latest_close=round(latest_close, 3),
            latest_rsi=round(latest_rsi, 2)
        )

        llm = ChatOpenAI(model="gpt-4", temperature=0.7)
        result = llm.predict(prompt)

        st.subheader("📈 分析結果")
        st.markdown(result)
