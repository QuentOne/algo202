# src/strategy/strat1.py

import backtrader as bt

class Strat1(bt.Strategy):
    """
    ATR-based Volatility Breakout Strategy:
    - Compute ATR for volatility measurement.
    - If today's close > (yesterday's close + atr_factor * ATR), go long.
    - Position size determined by risk_per_trade * broker.getvalue().
    - Stop-loss placed at (entry_price - stop_factor * ATR).
    """

    params = (
        ('atr_period', 15),       # ATR lookback
        ('atr_factor', 2),      # Breakout threshold in ATR multiples
        ('stop_factor', 8.0),     # Stop distance in ATR multiples
        ('risk_per_trade', 0.4), # Fraction of total capital to risk per trade
    )

    def __init__(self):
        # The Average True Range indicator
        self.atr = bt.indicators.AverageTrueRange(
            self.datas[0], period=self.p.atr_period
        )

    def next(self):
        # Need at least 2 data points (yesterday/today)
        if len(self) < 2:
            return

        # Current vs. previous close
        curr_close = self.datas[0].close[0]
        prev_close = self.datas[0].close[-1]
        curr_atr   = self.atr[0]

        # Only enter if we have no position open
        if not self.position:
            breakout_level = prev_close + self.p.atr_factor * curr_atr
            if curr_close > breakout_level:
                # Calculate our stop-loss
                stop_price = curr_close - (self.p.stop_factor * curr_atr)
                risk_per_share = curr_close - stop_price
                if risk_per_share <= 0:
                    return

                # Determine position size so that (risk_per_share * size) ~ risk capital
                cash = self.broker.getvalue()
                trade_risk = cash * self.p.risk_per_trade
                size = trade_risk / risk_per_share

                # Bracket order with no take-profit limit
                self.buy_bracket(
                    size=size,
                    limitprice=None,         # no profit target
                    price=curr_close,        # roughly a market order
                    stopprice=stop_price     # fixed stop-loss
                )
