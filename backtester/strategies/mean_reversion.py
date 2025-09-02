"""
"""
from .base import Strategy
import pandas as pd


class MeanReversionStrategy(Strategy):

    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        ...
