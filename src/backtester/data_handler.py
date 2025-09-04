"""Data handler module.

This module contains the DataHandler class, which streams historical market data from
Yahoo Finance and appends MarketEvents to the event queue.
"""

from typing import Deque, Iterable, Self

import pandas as pd
import yfinance as yf

from .events import Event, MarketEvent


class DataHandler:
    """Stream historical market data.

    Loads data from Yahoo Finance iterates over it to generate MarketEvents. Each
    datetime indexed row of data corresponds to a new market events that are appended to
    the event queue.
    """

    def __init__(
        self, tickers: str | list[str], start: str, end: str, interval: str = "1h"
    ) -> None:
        """Initialize the data handler.

        Args:
            tickers (list[str], str): Ticker(s) symbol to load historical data for.
            start (str): Start date for historical data (YYYY-MM-DD).
            end (str): End date for historical data (YYYY-MM-DD).
            interval (str, optional): Data frequency (e.g., "1h", "1d"). Defaults to
                "1h".

        Raises:
            ValueError: If data cannot be retrieved for the given parameters.
        """
        if isinstance(tickers, str):
            self.tickers: list[str] = [tickers]
        else:
            self.tickers: list[str] = tickers

        self.event_queue: Deque[Event] | None = None
        self.data: pd.DataFrame | None = yf.download(
            self.tickers,
            start=start,
            end=end,
            interval=interval,
            group_by="ticker",
            auto_adjust=True,
        )

        self._iter: Iterable = self.data.iterrows()

    def __iter__(self) -> Self:
        """Return the iterator interface.

        Returns:
            DataHandler (self): The iterator.
        """
        return self

    def __next__(self) -> None:
        """Generate the next MarketEvents and append them to the queue.

        Raises:
            RuntimeError: If the event queue has mot been set.
            StopIteration: When no more data is available.
        """
        datetime, row = next(self._iter)
        row_df = row.unstack(level=0)

        events = [
            MarketEvent(
                symbol=symbol,
                datetime=datetime,
                open=row_df.loc["Open", symbol],
                close=row_df.loc["Close", symbol],
            )
            for symbol in self.tickers
        ]

        if self.event_queue is None:
            raise RuntimeError("DataHandler: event_queue is not set")

        self.event_queue.extend(events)
