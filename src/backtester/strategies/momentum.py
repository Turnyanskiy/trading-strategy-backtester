"""Momentum strategies module.

This module implements a simple long-short momentum strategy following
Jegadeesh & Titman (1993). Stocks are ranked based on past returns over a
formation period and the 1st and 10th decile are held for a defined holding period.
"""

from collections import deque
from typing import Deque

import numpy as np
import pandas as pd

from ..events import MarketEvent, SignalEvent
from .base import Strategy


class SimpleMomentumStrategy(Strategy):
    """Simple momentum long-short strategy."""

    def __init__(self, tickers: str | list[str], j: int = 3, k: int = 3):
        """Initialize the strategy.

        Args:
            tickers (str | list[str]): Ticker(s) symbol to use strategy on.
            j (int): Formation period in number of periods.
            k (int): Trading period in number of periods.
        """
        super().__init__(tickers)
        self.j = j
        self.k = k

        self.tickers_history: dict[str, Deque[MarketEvent]] = {
            t: deque(maxlen=j) for t in tickers
        }

        self.current_datetime: pd.DatetimeIndex | None = None
        self.current_period: int = 0

        self.pending_signals: dict[str, deque[SignalEvent]] = {
            t: deque([SignalEvent("", 0)] * k, maxlen=k) for t in tickers
        }

    def generate_signal(self, event: MarketEvent) -> None:
        """Generate signals based on momentum strategy.

        This method performs the following steps:
        1. Exit positions that have completed the holding period.

        Formation period
        2. Once all tickers have sufficient history for a datetime, calculate
           past returns over j periods.
        3. Rank stocks into deciles;

        Trading period
        4. Enter long positions on 10th decile and short positions on 1st decile.
        5. Append signals to the event queue and track pending signals for exit in k
           periods.

        Args:
            event (MarketEvent): Market event for a specific ticker.
        """
        # Exit position after holding for k periods
        if self.pending_signals[event.symbol]:
            self.event_queue.append(self.pending_signals[event.symbol].popleft())

        # Enter formation period once all MarketEvents for a datetime is known
        if event.datetime != self.current_datetime:
            self.current_period += 1
            # Ensure at least j periods have passed
            if self.current_period >= self.j:
                # Compute j-period returns for each ticker
                tickers_returns = []
                for ticker in sorted(self.tickers):
                    history = self.tickers_history[ticker]
                    ticker_return = history[-1].close / history[0].close - 1
                    tickers_returns.append((ticker, ticker_return))

                returns_only = np.array([r for _, r in tickers_returns])

                # Get boundaries for the 1st and 10th decile of stock returns
                short_leg = np.percentile(returns_only, 10)
                long_leg = np.percentile(returns_only, 90)

                # Enter long/short positions on selected stocks.
                for ticker, j_period_return in tickers_returns:
                    if j_period_return <= short_leg:
                        self.event_queue.append(SignalEvent(ticker, -1))
                        self.pending_signals[ticker].append(SignalEvent(ticker, 1))
                    elif j_period_return >= long_leg:
                        self.event_queue.append(SignalEvent(ticker, 1))
                        self.pending_signals[ticker].append(SignalEvent(ticker, -1))

        self.tickers_history[event.symbol].append(event)
        self.current_datetime = event.datetime
