from langchain.prompts import PromptTemplate

def generate_prompt(data: dict) -> str:
    template = PromptTemplate.from_template("""
あなたはFX初心者向けのテクニカルトレード戦略アドバイザーです。
以下のデータとユーザーの希望スタイルを元に、最適な戦略とおすすめのFX業者1社を提案してください。

- 銘柄: {symbol}
- 期間: {start_date} 〜 {end_date}
- 現在価格: {latest_close}
- RSI: {latest_rsi}
- MACD: {latest_macd}, シグナル: {latest_macd_signal}
- ボリンジャーバンド: 上限={latest_bb_upper}, 下限={latest_bb_lower}
- ストキャスティクス: %K={latest_k}, %D={latest_d}
- ユーザーの希望スタイル: {user_style}

出力：
1. テクニカル分析結果
2. 勝率の高いエントリータイミング
3. ロング/ショート戦略
4. 損切り・利確ライン
5. 初心者への心構え
6. バックテスト評価（勝率、リスクリワード比など）
7. この戦略に最適なFX業者（名前と理由）を以下から1社提案：

[XM, AXIORY, みんなのFX, LIGHT FX, FXTF, マネックス証券, moomoo証券, 松井証券FX, SBI証券, 外為オンライン, GMOクリック証券]

形式：
【おすすめFX業者】：<業者名>  
【理由】：<理由>

""")
    return template.format(**data)
