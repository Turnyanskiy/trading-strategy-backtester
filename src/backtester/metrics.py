"""Metrics module.

This module contains performance metric functions for evaluating trading strategy
backtesting.
"""

import numpy as np
import pandas as pd


def volatility(
    period_returns: pd.Series, periods_per_year: float | None = None
) -> float:
    """Calculate the annualized volatility (standard deviation) of returns.

    Args:
        period_returns (pd.Series): Series of returns (decimal, e.g., 0.01 = 1%) with
            datetime index.
        periods_per_year (float, optional): Number of periods in a year. If None,
            inferred from datetime index.

    Returns:
        float: Annualized volatility of returns.
    """
    if periods_per_year is None:
        period_length = period_returns.index.to_series().diff().median()
        periods_per_year = pd.Timedelta(days=252) / period_length

    return period_returns.std() * np.sqrt(periods_per_year)


def sharpe_ratio(
    period_returns: pd.Series,
    risk_free: float = 0,
    periods_per_year: float | None = None,
) -> float:
    """Calculate annualized Sharpe ratio.

    Args:
        period_returns (pd.Series): Series of returns (decimal, e.g., 0.01 = 1%) with
            datetime index.
        risk_free (float, optional): Risk-free rate per period.
        periods_per_year (float, optional): Number of periods in a year. If None,
            inferred from datetime index.

    Returns:
        float: Annualized Sharpe ratio.
    """
    if periods_per_year is None:
        period_length = period_returns.index.to_series().diff().median()
        periods_per_year = pd.Timedelta(days=252) / period_length

    excess_returns = period_returns - risk_free
    return (
        excess_returns.mean()
        / volatility(period_returns, periods_per_year=periods_per_year)
    ) * np.sqrt(periods_per_year)


def max_drawdown(period_returns: pd.Series) -> float:
    """Calculate the maximum drawdown of a returns series.

    Args:
        period_returns (pd.Series): Series of returns (decimal, e.g., 0.01 = 1%).

    Returns:
        float: Maximum drawdown as a negative fraction (e.g., -0.2 for -20%).
    """
    cumulative = (1 + period_returns).cumprod()
    peak = cumulative.cummax()
    drawdown = (cumulative - peak) / peak
    return drawdown.min()


def alpha():
    """TODO: Implement this function."""
    ...


def beta():
    """TODO: Implement this function."""
    ...
