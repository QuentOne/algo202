#!/usr/bin/env python

import yfinance as yf
import pandas as pd
import backtrader as bt
from datetime import datetime
import os

from strategy.ema_strategy import Strat1

def download_to_csv(symbol, start, end, csv_file):
    """
    Download daily data with yfinance, flatten if multi-indexed,
    add OpenInterest=0, reorder columns, and write to CSV for GenericCSVData.
    """
    print(f"Downloading data for {symbol} from {start} to {end}...")
    df = yf.download(symbol, start=start, end=end)
    if df.empty:
        print("No data fetched. Check your Internet or symbol.")
        return False

    # Flatten multi-index columns if present
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[0] for col in df.columns]

    # Add OpenInterest if not present
    if 'OpenInterest' not in df.columns:
        df['OpenInterest'] = 0

    # Move 'Date' from index to a column
    df.reset_index(inplace=True)

    # Reorder columns: Date, Open, High, Low, Close, Volume, OpenInterest
    df = df[['Date','Open','High','Low','Close','Volume','OpenInterest']]

    # Convert 'Date' to string 'YYYY-MM-DD' if datetime
    if pd.api.types.is_datetime64_any_dtype(df['Date']):
        df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')

    df.to_csv(csv_file, index=False)
    print(f"Data saved to {csv_file}")
    return True

def main():
    symbol = "BTC-USD"  # Example: a volatile crypto ticker on yfinance
    start_date = "2024-01-01"
    end_date   = "2025-01-01"
    csv_file   = "BTC.csv"

    # (A) Download & write CSV
    success = download_to_csv(symbol, start_date, end_date, csv_file)
    if not success or not os.path.exists(csv_file):
        return

    # (B) Create Cerebro
    cerebro = bt.Cerebro()
    cerebro.broker.setcommission(commission=0.005)
    # (C) Load CSV using GenericCSVData
    data = bt.feeds.GenericCSVData(
        dataname=csv_file,
        dtformat='%Y-%m-%d',
        timeframe=bt.TimeFrame.Days,
        time=-1,                   # No separate Time column
        dtcolumn=0,                # 'Date'
        opencolumn=1,             # 'Open'
        highcolumn=2,
        lowcolumn=3,
        closecolumn=4,
        volumecolumn=5,
        openinterestcolumn=6
    )
    cerebro.adddata(data)

    # (D) Add the Volatility Breakout Strategy
    # Adjust parameters if desired
    cerebro.addstrategy(Strat1, 
                        atr_period=15, 
                        atr_factor=1, 
                        stop_factor=8.0, 
                        risk_per_trade=0.4)

    # (E) Initial capital
    cerebro.broker.setcash(100000.0)

    # (F) Run
    print("Starting Portfolio Value: %.2f" % cerebro.broker.getvalue())
    cerebro.run()
    print("Final Portfolio Value: %.2f" % cerebro.broker.getvalue())

    # (G) Plot results (optional)
    cerebro.plot()

if __name__ == "__main__":
    main()
