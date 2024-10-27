import yfinance as yf

data = yf.download("AAPL", start="2024-01-01", end=None)
print(data)