# ai_finance_app.py

import streamlit as st
from datetime import datetime
from modules.technical import analyze_crypto
from modules.sentiment import run_sentiment_analysis
from modules.fundamentals import get_fundamental_data
from modules.onchain import analyze_onchain  # فرض بر این است که این ماژول وجود دارد

# تنظیمات صفحه
st.set_page_config(page_title="Crypto Market Smart Analysis", layout="wide")
st.title("📊 Smart Crypto Market Analysis Platform")

# بخش ورودی‌ها
st.sidebar.header("🛠 Input Settings")
symbol = st.sidebar.selectbox("🔍 Select Cryptocurrency", ["BTC", "ETH", "XRP"], index=0)
start_date = st.sidebar.date_input("From Date", datetime(2024, 6, 1))
end_date = st.sidebar.date_input("To Date", datetime.now())

st.sidebar.header("⚙️ Select Technical Indicators")
indicators = st.sidebar.multiselect(
    "Choose indicators:",
    options=["RSI", "MACD", "SMA 50", "SMA 200", "Bollinger Bands", "Ichimoku"],
    default=["RSI", "MACD", "SMA 200"]
)

run_analysis = st.sidebar.button("🚀 Run Full Analysis")

if run_analysis:
    st.header(f"📈 Full Analysis for {symbol}")

    # تبدیل تاریخ به رشته yyyy-mm-dd برای yf.download
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")

    # تحلیل تکنیکال
    with st.spinner("Running technical analysis..."):
        try:
            signal, price, trend, chart = analyze_crypto(symbol, indicators, start_date=start_date_str, end_date=end_date_str)
            st.subheader("💹 Technical Analysis")
            st.write(f"**Live Price:** ${price:.2f}")
            st.write(f"**Technical Signal:** {signal}")
            st.write(f"**Market Trend:** {trend}")
            st.pyplot(chart)
        except Exception as e:
            st.error(f"❌ Technical Analysis Error: {e}")

    # تحلیل فاندامنتال
    with st.spinner("Extracting fundamental data..."):
        try:
            fundamentals = get_fundamental_data(symbol)
            st.subheader("📊 Fundamental Analysis")
            st.write(fundamentals)
        except Exception as e:
            st.error(f"❌ Fundamental Analysis Error: {e}")

    # تحلیل احساسات و اخبار
    with st.spinner("Analyzing market sentiment and news..."):
        try:
            run_sentiment_analysis([symbol], start_date, end_date)
        except Exception as e:
            st.error(f"❌ Sentiment Analysis Error: {e}")

    # تحلیل آن‌چین
    with st.spinner("Analyzing on-chain data..."):
        try:
            onchain_df = analyze_onchain(symbol)
            st.subheader("🔗 On-Chain Analysis")
            st.dataframe(onchain_df)
        except Exception as e:
            st.error(f"❌ On-Chain Analysis Error: {e}")
