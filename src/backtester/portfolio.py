"""Portfolio module.

This module contains the Position and Portfolio classes, which track holdings,
cash, equity, and returns throughout the backtest. It processes events such as
FillEvents, SignalEvents, and MarketEvents, and provides summary metrics.
"""

from collections import defaultdict
from dataclasses import asdict, dataclass
from typing import Any, Deque

import pandas as pd

from backtester.metrics import max_drawdown, sharpe_ratio, volatility

from .events import Event, FillEvent, MarketEvent, OrderEvent, OrderType, SignalEvent


@dataclass(slots=True)
class Position:
    """Represents a single asset position.

    Attributes:
        quantity (float): Number of units held.
        average_cost (float): Average cost basis per unit.
        market_price (float): Latest observed market price.
    """

    quantity: float = 0
    average_cost: float = 0
    market_price: float = 0

    def on_fill_event(self, event: FillEvent) -> None:
        """Update position on fill.

        Args:
            event (FillEvent): Fill event containing executed quantity and cost.
        """
        new_quantity = self.quantity + event.quantity

        if new_quantity == 0:
            self.quantity = 0
            self.average_cost = 0
        else:
            self.average_cost = (
                self.average_cost * self.quantity + event.fill_cost
            ) / new_quantity
            self.quantity = new_quantity

    def on_market_event(self, event: MarketEvent) -> None:
        """Handle a market event by updating market price.

        Args:
            event (MarketEvent): Event containing the latest close price.
        """
        self.market_price = event.close


class Portfolio:
    """Track portfolio holdings, cash, equity, and returns.

    The Portfolio processes events (SignalEvent, MarketEvent, FillEvent) to update its
    state and generates a history of positions and portfolio value. The portfolio
    appends OrderEvents to the event queue when completing a SignalEvent. It also
    provides summary performance metrics.
    """

    def __init__(self, cash: int = 100000) -> None:
        """Initialize the portfolio.

        Args:
            cash (int, optional): Initial portfolio cash. Defaults to 100000.
        """
        self.event_queue: Deque[Event] | None = None

        self._inital_cash = cash
        self.cash = cash

        self.current_position: dict[str, Position] = defaultdict(Position)

        self._latest_market_event: MarketEvent | None = None
        self._position_history: list[dict] = []
        self._asset_history: dict[str, list[dict]] = defaultdict(list)

    # TODO: Risk management, position sizing considerations, Exit positions
    def on_signal_event(self, event: SignalEvent) -> None:
        """Handle a signal event by generating an order.

        Args:
            event (SignalEvent): Trading signal with direction/strength.

        Raises:
            RuntimeError: If the event queue is not set.
        """
        if self.event_queue is None:
            raise RuntimeError("Portfolio: event_queue is not set")

        self.event_queue.append(
            OrderEvent(event.symbol, OrderType.MARKET, int(10 * event.strength))
        )

    def on_market_event(self, event: MarketEvent) -> None:
        """Handle a market event by updating porfolio valuation & saving positions.

        Args:
            event (MarketEvent): Latest market event with pricing information.
        """
        self._latest_market_event = event
        self.current_position[event.symbol].on_market_event(event)

        position_snapshot = {
            "datetime": event.datetime,
            "cash": self.cash,
        }

        holding = 0
        for symbol, position in self.current_position.items():
            asset_snapshot = asdict(position)
            asset_snapshot["datetime"] = event.datetime
            self._asset_history[symbol].append(asset_snapshot)

            holding += position.quantity * position.market_price

        position_snapshot["holding"] = holding
        position_snapshot["equity"] = holding + self.cash

        self._position_history.append(position_snapshot)

    def on_fill_event(self, event: FillEvent) -> None:
        """Handle a fill event by updating portfolio costs.

        Args:
            event (FillEvent): Fill event with executed order information.
        """
        self.current_position[event.symbol].on_fill_event(event)
        self.cash -= event.fill_cost

    def get_position_history(self) -> dict[str, pd.DataFrame]:
        """Get historical portfolio and asset snapshots.

        Returns:
            dict[str, pd.DataFrame]:
                - 'portfolio': DataFrame of portfolio-level cash, holding,
                  equity, and returns.
                - '<ticker symbol>': DataFrame for tracked asset.
        """
        history = {
            "portfolio": pd.DataFrame(self._position_history).set_index("datetime"),
            **{
                ticker: pd.DataFrame(history).set_index("datetime")
                for ticker, history in self._asset_history.items()
            },
        }

        history["portfolio"]["period returns"] = (
            history["portfolio"]["equity"].pct_change()
        ).fillna(0)

        return history

    def summary(self) -> dict[str, Any]:
        """Calculate summary performance metrics.

        Returns:
            dict[str, Any]:
                - 'Cumulative Return': Decimal representing return for backtest period.
                - 'Annulized Volatility': Annulized standard devation for returns.
                - 'Annulized Sharpe Ratio': Annulized sharpe ratio for backtest.
                - 'Max Drawdown': Max drawdown for backtest.
        """
        history = self.get_position_history()
        returns: pd.Series = history["portfolio"]["period returns"]

        return {
            "Cumulative Return": returns.cumprod(),
            "Annulized Volatility": volatility(returns),
            "Annulized Sharpe Ratio": sharpe_ratio(returns),
            "Max Drawdown": max_drawdown(returns),
        }
