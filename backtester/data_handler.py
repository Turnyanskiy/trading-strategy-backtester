"""Data loader class."""
import yfinance as yf
from .events import Event
from typing import Deque
from .events import MarketEvent

# TODO: Allow datahandler to mange sevral tickers.
class DataHandler:
    """"""

    def __init__(self, ticker: str, start: str, end: str, interval: str = "1h") -> None:
        """"""
        self.ticker: yf.Ticker = yf.Ticker(ticker)
        self.event_queue: Deque[Event] | None = None
        self.data = self.ticker.history(start=start, end=end, interval=interval)

        self._iter = self.data.itertuples(index=True)
    def __iter__(self):
        return self

    def __next__(self) -> None:
        row = next(self._iter)
        event = MarketEvent(
            symbol=self.ticker.ticker,
            datetime=row.Index,
            open=row.Open,
            close=row.Close
        )

        if self.event_queue is None:
            raise RuntimeError("DataHandler: event_queue is not set")

        self.event_queue.append(event)

