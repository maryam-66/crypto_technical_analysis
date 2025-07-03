import requests

def get_fundamental_data(symbol):
    symbol_map = {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "XRP": "ripple"
    }
    
    coin_id = symbol_map.get(symbol, "bitcoin")
    
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        market_data = data.get("market_data", {})
        
        fundamentals = {
            "Market Cap (USD)": market_data.get("market_cap", {}).get("usd", "N/A"),
            "24h Volume (USD)": market_data.get("total_volume", {}).get("usd", "N/A"),
            "24h Price Change (%)": market_data.get("price_change_percentage_24h", "N/A"),
            "Market Cap Rank": data.get("market_cap_rank", "N/A"),
            "Circulating Supply": market_data.get("circulating_supply", "N/A"),
        }
        
        return fundamentals
    
    except Exception as e:
        return {"error": f"خطا در دریافت داده‌های فاندامنتال: {e}"}
