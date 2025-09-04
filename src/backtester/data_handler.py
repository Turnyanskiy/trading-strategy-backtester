"""Data handler module.

This module contains the DataHandler class, which streams historical market data from
Yahoo Finance and appends MarketEvents to the event queue.
"""

from typing import Deque, Self

import yfinance as yf

from .events import Event, MarketEvent


# TODO: Allow datahandler to manage several tickers.
class DataHandler:
    """Stream historical market data.

    Loads data from Yahoo Finance iterates over it to generate MarketEvents. Each
    datetime indexed row of data corresponds to a new market event that is appended to
    the event queue.
    """

    def __init__(self, ticker: str, start: str, end: str, interval: str = "1h") -> None:
        """Initialize the data handler.

        Args:
            ticker (str): Ticker symbol to load historical data for.
            start (str): Start date for historical data (YYYY-MM-DD).
            end (str): End date for historical data (YYYY-MM-DD).
            interval (str, optional): Data frequency (e.g., "1h", "1d"). Defaults to
                "1h".

        Raises:
            ValueError: If data cannot be retrieved for the given parameters.
        """
        self.ticker: yf.Ticker = yf.Ticker(ticker)
        self.event_queue: Deque[Event] | None = None
        self.data = self.ticker.history(start=start, end=end, interval=interval)

        self._iter = self.data.itertuples(index=True)

    def __iter__(self) -> Self:
        """Return the iterator interface.

        Returns:
            DataHandler (self): The iterator.
        """
        return self

    def __next__(self) -> None:
        """Generate the next MarketEvent and append it to the queue.

        Raises:
            RuntimeError: If the event queue has mot been set.
            StopIteration: When no more data is available.
        """
        row = next(self._iter)
        event = MarketEvent(
            symbol=self.ticker.ticker,
            datetime=row.Index,
            open=row.Open,
            close=row.Close,
        )

        if self.event_queue is None:
            raise RuntimeError("DataHandler: event_queue is not set")

        self.event_queue.append(event)
