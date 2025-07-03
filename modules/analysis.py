def analyze_crypto(symbol, indicators):
    yf_symbol_map = {
        "BTC": "BTC-USD",
        "ETH": "ETH-USD",
        "XRP": "XRP-USD"
    }
    yf_symbol = yf_symbol_map.get(symbol)
    if yf_symbol is None:
        raise ValueError("نماد پشتیبانی نمی‌شود.")
    
    data = yf.download(yf_symbol, period="1mo", interval="1h", progress=False)
    if data.empty:
        raise ValueError("داده‌ای دریافت نشد.")
    
    close = data['Close']
    if len(close.shape) > 1:
        close = close.squeeze()

    fig, ax = plt.subplots(figsize=(12,6))
    ax.plot(data.index, close, label="قیمت بسته شدن", color='black')
    
    signal = "خنثی"
    
    # محاسبه و رسم اندیکاتورها بر اساس انتخاب کاربر
    if "RSI" in indicators:
        rsi = RSIIndicator(close).rsi()
        ax.plot(data.index, rsi, label="RSI")
        last_rsi = rsi.iloc[-1]
        if last_rsi > 70:
            signal = "فروش (Overbought)"
        elif last_rsi < 30:
            signal = "خرید (Oversold)"
    
    if "MACD" in indicators:
        macd_indicator = MACD(close)
        macd = macd_indicator.macd()
        signal_line = macd_indicator.macd_signal()
        ax.plot(data.index, macd, label="MACD")
        ax.plot(data.index, signal_line, label="Signal Line")
        if macd.iloc[-1] > signal_line.iloc[-1]:
            signal = "خرید (MACD کراس مثبت)"
        else:
            signal = "فروش (MACD کراس منفی)"
    
    sma50 = None
    sma200 = None
    
    if "SMA 50" in indicators:
        sma50 = SMAIndicator(close, window=50).sma_indicator()
        ax.plot(data.index, sma50, label="SMA 50")
    
    if "SMA 200" in indicators:
        sma200 = SMAIndicator(close, window=200).sma_indicator()
        ax.plot(data.index, sma200, label="SMA 200")
    
    if "Bollinger Bands" in indicators:
        bb = BollingerBands(close)
        ax.plot(data.index, bb.bollinger_hband(), label="BB بالا", linestyle='--')
        ax.plot(data.index, bb.bollinger_lband(), label="BB پایین", linestyle='--')
    
    if "Ichimoku" in indicators:
        nine_high = data['High'].rolling(window=9).max()
        nine_low = data['Low'].rolling(window=9).min()
        tenkan_sen = (nine_high + nine_low) / 2

        period26_high = data['High'].rolling(window=26).max()
        period26_low = data['Low'].rolling(window=26).min()
        kijun_sen = (period26_high + period26_low) / 2

        senkou_span_a = ((tenkan_sen + kijun_sen) / 2).shift(26)
        senkou_span_b = ((data['High'].rolling(window=52).max() + data['Low'].rolling(window=52).min()) / 2).shift(26)

        ax.plot(data.index, tenkan_sen, label="Tenkan-sen")
        ax.plot(data.index, kijun_sen, label="Kijun-sen")
        ax.plot(data.index, senkou_span_a, label="Senkou Span A")
        ax.plot(data.index, senkou_span_b, label="Senkou Span B")
        
        if tenkan_sen.iloc[-1] > kijun_sen.iloc[-1]:
            signal = "صعودی (Ichimoku)"
        else:
            signal = "نزولی (Ichimoku)"

    # تحلیل روند کلی ساده با استفاده از SMA200 و SMA50
    trend = "خنثی"
    if sma50 is not None and sma200 is not None:
        if sma50.iloc[-1] > sma200.iloc[-1]:
            trend = "روند صعودی"
        elif sma50.iloc[-1] < sma200.iloc[-1]:
            trend = "روند نزولی"
    
    ax.set_title(f"تحلیل تکنیکال {symbol}")
    ax.legend()
    plt.tight_layout()
    
    current_price = close.iloc[-1]
    
    return signal, current_price, trend, fig
