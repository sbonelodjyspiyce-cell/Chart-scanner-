import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Forex AI Scanner Mobile", page_icon="📱", layout="wide")

# -- STYLE LIKE MOBILE APP --
st.markdown("""
<style>
.metric-card {background:#1e1e1e; padding:15px; border-radius:12px; border:1px solid #333;}
.big {font-size:28px; font-weight:bold;}
</style>
""", unsafe_allow_html=True)

st.title("📱 Forex AI Scanner")
st.caption("Overview of active pairs • Latest signals at a glance")

def ema(s,p): return s.ewm(span=p, adjust=False).mean()
def rsi(s,p=14):
    d=s.diff(); g=d.clip(lower=0); l=-d.clip(upper=0)
    ag=g.ewm(alpha=1/p, adjust=False).mean(); al=l.ewm(alpha=1/p, adjust=False).mean()
    return 100-(100/(1+ag/al))

symbols = {
    "XAUUSD": "XAUUSD=X", "EURUSD": "EURUSD=X", "GBPUSD": "GBPUSD=X",
    "USDJPY": "USDJPY=X", "US30": "^DJI", "NAS100": "^IXIC",
    "BTCUSD": "BTC-USD", "ETHUSD": "ETH-USD"
}

tf = st.selectbox("Timeframe", ["1m","5m","15m","1h","4h"], index=1)

if st.button("🚀 Scan Market Now", use_container_width=True):
    results=[]
    with st.spinner("Scanning..."):
        for name, yf_sym in symbols.items():
            try:
                df = yf.download(yf_sym, period="2d", interval=tf, progress=False, auto_adjust=True)
                if len(df)<40: continue
                if hasattr(df.columns,'get_level_values'): df.columns=df.columns.get_level_values(0)
                df['FAST']=ema(df['Close'],20); df['SLOW']=ema(df['Close'],50); df['RSI']=rsi(df['Close'])
                last=df.iloc[-1]; prev=df.iloc[-2]
                buy = prev['FAST']<prev['SLOW'] and last['FAST']>last['SLOW']
                sell = prev['FAST']>prev['SLOW'] and last['FAST']<last['SLOW']
                signal = "BUY" if buy and last['RSI']>50 else "SELL" if sell and last['RSI']<50 else "NEUTRAL"
                trend = "Bullish" if last['FAST']>last['SLOW'] else "Bearish"
                results.append({"Pair":name,"Price":float(last['Close']),"Signal":signal,"Trend":trend,"RSI":round(float(last['RSI']),1)})
            except: continue
    
    if results:
        df_r = pd.DataFrame(results)
        # DASHBOARD
        c1,c2,c3 = st.columns(3)
        c1.metric("Active Pairs", len(df_r))
        c2.metric("BUY Signals", len(df_r[df_r.Signal=="BUY"]))
        c3.metric("SELL Signals", len(df_r[df_r.Signal=="SELL"]))
        
        st.divider()
        st.subheader("📊 1. Dashboard - Latest Signals")
        st.dataframe(df_r, use_container_width=True, hide_index=True)

        for row in results:
            if row['Signal']!="NEUTRAL":
                if row['Signal']=="BUY":
                    st.success(f"✅ {row['Pair']} - {row['Signal']} @ {row['Price']} | RSI {row['RSI']} | {row['Trend']}")
                else:
                    st.error(f"🔻 {row['Pair']} - {row['Signal']} @ {row['Price']} | RSI {row['RSI']} | {row['Trend']}")
    else:
        st.warning("No data - try 5m or 15m timeframe")
else:
    st.info("👆 Click Scan to see Overview of active pairs")
    st.markdown("**Main Screens:**\n- Dashboard\n- Signals\n- Gold Focus")
