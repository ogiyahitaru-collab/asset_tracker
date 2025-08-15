import yfinance as yf
import json

# 対象銘柄（必要に応じて追加）
TICKERS = ["5406.T", "7203.T"]
PRICES_FILE = "prices.json"

def fetch_prices(tickers):
    prices = {}
    for ticker in tickers:
        data = yf.Ticker(ticker)
        hist = data.history(period="1d")
        if not hist.empty:
            price = round(hist["Close"].iloc[-1])
            prices[ticker] = price
            print(f"{ticker}: {price} 円")
        else:
            print(f"{ticker}: データなし")
    return prices

if __name__ == "__main__":
    prices = fetch_prices(TICKERS)
    with open(PRICES_FILE, "w", encoding="utf-8") as f:
        json.dump(prices, f, ensure_ascii=False, indent=2)
    print(f"✅ 株価を {PRICES_FILE} に保存しました")
