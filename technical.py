# modules/technical.py

import yfinance as yf
import matplotlib.pyplot as plt
from ta.momentum import RSIIndicator
from ta.trend import MACD, SMAIndicator
from ta.volatility import BollingerBands
import pandas as pd


def analyze_crypto(symbol, indicators, start_date=None, end_date=None):
    yf_symbol_map = {
        "BTC": "BTC-USD",
        "ETH": "ETH-USD",
        "XRP": "XRP-USD"
    }
    yf_symbol = yf_symbol_map.get(symbol)
    if yf_symbol is None:
        raise ValueError("Unsupported symbol")

    data = yf.download(yf_symbol, period="1mo", interval="1h", progress=False, auto_adjust=True)
    if data.empty:
        raise ValueError("No data received")

    data = data.dropna()

    close = data['Close']
    if isinstance(close, pd.DataFrame):
        close = close.squeeze()  # اگر DataFrame بود به Series تبدیل کن

    fig, axs = plt.subplots(3, 1, figsize=(14, 10), sharex=True, gridspec_kw={'height_ratios': [2, 1, 1]})

    # نمودار قیمت نهایی
    axs[0].plot(data.index, close, label="Closing Price", color='black', linewidth=1.5)
    axs[0].set_title(f"Technical Analysis for {symbol}", fontsize=18, fontweight='bold')
    axs[0].set_ylabel("Price (USD)", fontsize=14)

    signal = "Neutral"
    trend = "Neutral"

    if "RSI" in indicators:
        rsi_series = RSIIndicator(close=close).rsi()
        axs[1].plot(data.index, rsi_series, label="RSI", color='blue', linewidth=1.5)
        axs[1].axhline(70, color='red', linestyle='--', linewidth=1)
        axs[1].axhline(30, color='green', linestyle='--', linewidth=1)
        axs[1].set_ylabel("RSI", fontsize=14)
        axs[1].set_title("Relative Strength Index (RSI)", fontsize=14, fontweight='bold')
        last_rsi = rsi_series.dropna().iloc[-1]
        if last_rsi > 70:
            signal = "Sell (RSI Overbought)"
        elif last_rsi < 30:
            signal = "Buy (RSI Oversold)"

    if "MACD" in indicators:
        macd = MACD(close=close)
        macd_line = macd.macd()
        signal_line = macd.macd_signal()
        axs[2].plot(data.index, macd_line, label="MACD", color='purple', linewidth=1.5)
        axs[2].plot(data.index, signal_line, label="Signal Line", color='orange', linewidth=1.5)
        axs[2].set_ylabel("MACD", fontsize=14)
        axs[2].set_title("Moving Average Convergence Divergence (MACD)", fontsize=14, fontweight='bold')
        if not macd_line.dropna().empty and not signal_line.dropna().empty:
            last_macd = macd_line.dropna().iloc[-1]
            last_signal = signal_line.dropna().iloc[-1]
            if last_macd > last_signal:
                signal = "Buy (MACD Crossover)"
            else:
                signal = "Sell (MACD Crossover)"

    sma50 = None
    sma200 = None
    if "SMA 50" in indicators:
        sma50 = SMAIndicator(close=close, window=50).sma_indicator()
        axs[0].plot(data.index, sma50, label="SMA 50", linestyle='--', color='blue', linewidth=1.2)
    if "SMA 200" in indicators:
        sma200 = SMAIndicator(close=close, window=200).sma_indicator()
        axs[0].plot(data.index, sma200, label="SMA 200", linestyle='--', color='red', linewidth=1.2)

    if sma50 is not None and sma200 is not None:
        if not sma50.dropna().empty and not sma200.dropna().empty:
            last_sma50 = sma50.dropna().iloc[-1]
            last_sma200 = sma200.dropna().iloc[-1]
            if last_sma50 > last_sma200:
                trend = "Uptrend"
            elif last_sma50 < last_sma200:
                trend = "Downtrend"

    if "Bollinger Bands" in indicators:
        bb = BollingerBands(close=close)
        upper_band = bb.bollinger_hband()
        lower_band = bb.bollinger_lband()
        axs[0].plot(data.index, upper_band, label="BB Upper", linestyle='-', color='green', linewidth=1.2)
        axs[0].plot(data.index, lower_band, label="BB Lower", linestyle='-', color='red', linewidth=1.2)

    if "Ichimoku" in indicators:
        high = data['High']
        low = data['Low']
        if isinstance(high, pd.DataFrame):
            high = high.squeeze()
        if isinstance(low, pd.DataFrame):
            low = low.squeeze()

        high9 = high.rolling(window=9).max()
        low9 = low.rolling(window=9).min()
        tenkan_sen = (high9 + low9) / 2

        high26 = high.rolling(window=26).max()
        low26 = low.rolling(window=26).min()
        kijun_sen = (high26 + low26) / 2

        span_a = ((tenkan_sen + kijun_sen) / 2).shift(26)
        span_b = ((high.rolling(window=52).max() + low.rolling(window=52).min()) / 2).shift(26)

        axs[0].plot(data.index, tenkan_sen, label="Tenkan-sen", linestyle='-.', color='orange', linewidth=1.5)
        axs[0].plot(data.index, kijun_sen, label="Kijun-sen", linestyle='-.', color='blue', linewidth=1.5)
        axs[0].plot(data.index, span_a, label="Senkou Span A", linestyle='-', color='green', linewidth=1.5)
        axs[0].plot(data.index, span_b, label="Senkou Span B", linestyle='-', color='red', linewidth=1.5)

        last_tenkan = tenkan_sen.dropna().iloc[-1] if not tenkan_sen.dropna().empty else None
        last_kijun = kijun_sen.dropna().iloc[-1] if not kijun_sen.dropna().empty else None

        if last_tenkan is not None and last_kijun is not None:
            if last_tenkan > last_kijun:
                signal = "Bullish (Ichimoku)"
            else:
                signal = "Bearish (Ichimoku)"
        else:
            signal = "Neutral (Ichimoku data insufficient)"

    for ax in axs:
        ax.legend(fontsize=11)
        ax.grid(True, linestyle='--', alpha=0.5)
        ax.tick_params(axis='both', which='major', labelsize=11)

    plt.setp(axs[-1].xaxis.get_majorticklabels(), rotation=45, ha='right', fontsize=11)
    axs[-1].set_xlabel("Date", fontsize=14)
    plt.tight_layout()

    return signal, close.iloc[-1], trend, fig
