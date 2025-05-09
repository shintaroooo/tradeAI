import pandas as pd

def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df['SMA_14'] = df['Close'].rolling(window=14).mean()
    df['RSI'] = 100 - (100 / (1 + (df['Close'].diff().clip(lower=0).rolling(14).mean() /
                                  df['Close'].diff().clip(upper=0).abs().rolling(14).mean())))
    df['EMA12'] = df['Close'].ewm(span=12, adjust=False).mean()
    df['EMA26'] = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = df['EMA12'] - df['EMA26']
    df['MACD_signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['BB_MID'] = df['Close'].rolling(window=20).mean()
    df['BB_STD'] = df['Close'].rolling(window=20).std()
    df['BB_UPPER'] = df['BB_MID'] + (df['BB_STD'] * 2)
    df['BB_LOWER'] = df['BB_MID'] - (df['BB_STD'] * 2)
    low_14 = df['Low'].rolling(window=14).min()
    high_14 = df['High'].rolling(window=14).max()
    df['%K'] = 100 * ((df['Close'] - low_14) / (high_14 - low_14))
    df['%D'] = df['%K'].rolling(window=3).mean()
    return df