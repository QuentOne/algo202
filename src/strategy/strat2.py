def generate_signal(prices):
    short_window = 50
    long_window = 200
    if len(prices) < long_window:
        return "HOLD"
    short_ma = sum(prices[-short_window:]) / short_window
    long_ma = sum(prices[-long_window:]) / long_window
    if short_ma > long_ma:
        return "BUY"
    elif short_ma < long_ma:
        return "SELL"
    else:
        return "HOLD"
if __name__ == "__main__":
    sample_prices = [100 + i for i in range(300)]
    signal = generate_signal(sample_prices)
    print(f"Signal: {signal}")