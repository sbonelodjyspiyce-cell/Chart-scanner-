import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
st.set_page_config(page_title="Chart Scanner", layout="wide")
st.title("📈 Free Chart Scanner - No Limits")
market = st.selectbox("Choose Market", ["FOREX", "STOCKS", "CRYPTO", "ALL"])
timeframe = st.selectbox("Timeframe", ["1m", "5m", "15m", "1h", "1d"])
forex = ["XAUUSD=X", "EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X"]
stocks = ["AAPL", "NVDA", "TSLA", "MSFT", "GOOGL", "META"]
crypto = ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD"]
if market == "FOREX": symbols = forex
elif market == "STOCKS": symbols = stocks
elif market == "CRYPTO": symbols = crypto
else: symbols = forex+stocks+crypto
if st.button("🔍 SCAN NOW"):
    results=[]
    for sym in symbols:
        try:
            df = yf.download(sym, period="7d", interval=timeframe, progress=False)
            if len(df)<60: continue
            if hasattr(df.columns,'get_level_values'): df.columns=df.columns.get_level_values(0)
            df['FAST']=ta.ema(df['Close'],20)
            df['SLOW']=ta.ema(df['Close'],50)
            df['RSI']=ta.rsi(df['Close'],14)
            last=df.iloc[-1]; prev=df.iloc[-2]
            buy = prev['FAST']<prev['SLOW'] and last['FAST']>last['SLOW'] and last['RSI']>50
            sell = prev['FAST']>prev['SLOW'] and last['FAST']<last['SLOW'] and last['RSI']<50
            if buy or sell:
                results.append({"Symbol":sym,"Price":round(float(last['Close']),2),"Signal":"BUY" if buy else "SELL","RSI":round(float(last['RSI']),1)})
        except: continue
    if results:
        st.dataframe(pd.DataFrame(results), use_container_width=True)
    else:
        st.warning("No BUY/SELL signals right now on "+timeframe)
