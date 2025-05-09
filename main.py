import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

from langchain.chat_models import ChatOpenAI

from technicals import calculate_indicators
from prompt_generator import generate_prompt
from fx_recommender import get_broker_list
from utils import extract_broker_recommendation, remove_broker_section

# .env読み込み
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# Streamlit UI
st.set_page_config(page_title="テクニカルトレード戦略AI", page_icon="💹")
st.title("テクニカルトレード戦略AI")

# 入力：銘柄と期間
# よく使われる銘柄リスト（プリセット）
preset_options = {
    "USD/JPY（米ドル円）": "USDJPY=X",
    "EUR/USD（ユーロドル）": "EURUSD=X",
    "GBP/JPY（英ポンド円）": "GBPJPY=X",
    "BTC/USD（ビットコイン）": "BTC-USD",
    "日経平均株価": "^N225",
    "ナスダック100": "^NDX",
    "S&P500": "^GSPC",
    "トヨタ自動車": "7203.T",
    "Apple": "AAPL",
    "Amazon": "AMZN"
}

# 銘柄入力UI
selected_label = st.selectbox("📌 よく使われる銘柄を選択", list(preset_options.keys()))
symbol_default = preset_options[selected_label]
custom_symbol = st.text_input("✍️ 任意の銘柄コードを入力（上書き可能）", value=symbol_default)

with st.expander("🔍 銘柄コードの調べ方（クリックで展開）"):
    st.markdown("""
    [Yahoo!ファイナンス](https://finance.yahoo.co.jp/) で検索してください。例：
    - 米ドル/円 → `USDJPY=X`
    - ユーロ/ドル → `EURUSD=X`
    - ビットコイン → `BTC-USD`
    - 日経平均 → `^N225`
    - トヨタ → `7203.T`
    """)

start_date = st.date_input("開始日", datetime(2021, 1, 1))
end_date = st.date_input("終了日", datetime.today())

# ユーザースタイル
user_style = st.selectbox("あなたのトレードスタイル", [
    "初心者向け", "短期", "中期", "長期", "スキャルピング", "テクニカル分析", "自動売買", "資産運用"
])

if st.button("分析を開始する"):
    with st.spinner("データ取得中..."):
        data = yf.download(custom_symbol, start=start_date, end=end_date)

    if data.empty:
        st.error("データが取得できませんでした。")
    else:
        data = calculate_indicators(data)
        latest = data.iloc[-1]

        prompt_input = {
            "symbol": custom_symbol,
            "start_date": start_date,
            "end_date": end_date,
            "latest_close": round(latest['Close'], 3),
            "latest_rsi": round(latest['RSI'], 2),
            "latest_macd": round(latest['MACD'], 3),
            "latest_macd_signal": round(latest['MACD_signal'], 3),
            "latest_bb_upper": round(latest['BB_UPPER'], 3),
            "latest_bb_lower": round(latest['BB_LOWER'], 3),
            "latest_k": round(latest['%K'], 1),
            "latest_d": round(latest['%D'], 1),
            "user_style": user_style
        }

        prompt = generate_prompt(prompt_input)

        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        with st.spinner("🧠 AIが分析中です。数秒お待ちください..."):
            result = llm.predict(prompt)

        # 業者レコメンド抽出
        broker_name, broker_reason = extract_broker_recommendation(result)
        analysis_only = remove_broker_section(result)

        # 分析結果のみ表示
        st.subheader("📈 分析結果")
        st.markdown(analysis_only)

        # FX業者の表示（重複しない）
        if broker_name:
            st.markdown(f"### {broker_name}")
            st.markdown(f"📝 理由: {broker_reason}")

            for broker in get_broker_list():
                if broker_name in broker["名前"]:
                    st.markdown(f"[👉 {broker_name}に申し込む（公式サイト）]({broker['リンク']})")
                    break
        else:
            st.warning("FX業者の推薦が取得できませんでした。")

st.markdown("""
---
<div style="text-align: center; font-size: 0.85em; color: gray;">
⚠️ 本サービスは、AIによる分析結果を提供するものであり、投資判断や売買を推奨するものではありません。<br>
FXおよびその他の金融商品は元本保証がなく、損失が生じるリスクがあります。<br>
投資判断は必ずご自身の責任で行ってください。
</div>
""", unsafe_allow_html=True)

