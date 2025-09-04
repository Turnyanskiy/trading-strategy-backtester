""""""
from dataclasses import asdict, dataclass
from backtester.metrics import volatility, sharpe_ratio, max_drawdown
from .events import Event, FillEvent, MarketEvent, SignalEvent, OrderEvent, OrderType
from typing import Deque
import pandas as pd
from collections import defaultdict
from typing import Any

@dataclass(slots=True)
class Position:
    quantity: float = 0
    average_cost: float = 0
    market_price: float = 0

    def on_fill_event(self, event: FillEvent) -> None:
        """"""
        new_quantity = self.quantity + event.quantity

        if new_quantity == 0:
            self.quantity = 0
            self.average_cost = 0
        else:
            self.average_cost = (self.average_cost * self.quantity + event.fill_cost) / new_quantity
            self.quantity = new_quantity

    def on_market_event(self, event: MarketEvent) -> None:
        self.market_price = event.close


class Portfolio:
    """"""
    def __init__(self, cash: int = 100000) -> None:
        """"""
        self.event_queue: Deque[Event] | None = None
        
        self._inital_cash = cash
        self.cash = cash

        self.current_position: dict[str, Position] = defaultdict(Position)

        self._latest_market_event: MarketEvent | None = None
        self._position_history: list[dict] = []
        self._asset_history: dict[str, list[dict]] = defaultdict(list)

    # TODO: Risk management, position sizing considerations, Exit positions
    def on_signal_event(self, event: SignalEvent) -> None:
        """"""
        if self.event_queue is None:
            raise RuntimeError("Portfolio: event_queue is not set")

        self.event_queue.append(OrderEvent(event.symbol, OrderType.MARKET, int(10 * event.strength)))

    # TODO: Improve position storing data structure
    # Take a snapshot of current state at the timeindex.
    def on_market_event(self, event: MarketEvent) -> None:
        """"""
        self._latest_market_event = event
        self.current_position[event.symbol].on_market_event(event)
        
        position_snapshot = {
            'datetime': event.datetime,
            'cash': self.cash,
        }
        
        holding = 0
        for symbol, position  in self.current_position.items():
            asset_snapshot = asdict(position)
            asset_snapshot['datetime'] = event.datetime
            self._asset_history[symbol].append(asset_snapshot)

            holding += position.quantity * position.market_price
        
        position_snapshot['holding'] = holding
        position_snapshot['equity'] = holding + self.cash

        self._position_history.append(position_snapshot)


    def on_fill_event(self, event: FillEvent) -> None:
        """"""
        self.current_position[event.symbol].on_fill_event(event)
        self.cash -= event.fill_cost
    

    def get_position_history(self) -> dict[str, pd.DataFrame]:
        """"""
        history = {
            'portfolio': pd.DataFrame(self._position_history).set_index('datetime'),
            **{ticker: pd.DataFrame(history).set_index('datetime') for ticker, history in self._asset_history.items()}
        }
        history['portfolio']['period returns'] = (history['portfolio']['equity'].pct_change()).fillna(0)
        return history

    def summary(self) -> dict[str, Any]:
        history = self.get_position_history()
        returns: pd.Series = history['portfolio']['period returns']

        return {
            'Cumulative Return': returns.sum(),
            'Annulized Volatility (s.d.)': volatility(returns),
            'Annulized Sharpe Ratio': sharpe_ratio(returns),
            'Max Drawdown': max_drawdown(returns)
        }
