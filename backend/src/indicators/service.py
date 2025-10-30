from typing import Dict, List, Any, Optional
import pandas as pd
from .ta_lib_adapter import TalibAdapter

class IndicatorService:
    """
    指标服务，提供统一的接口来访问各种技术指标
    """
    def __init__(self):
        self._indicators = {}
        self._load_available_indicators()

    def _load_available_indicators(self):
        """
        加载可用的指标库
        """
        # 使用TA-Lib适配器
        if TalibAdapter.is_available():
            self.talib_available = True
            # 注册TA-Lib指标
            self._indicators.update({
                'SMA': self._sma,
                'EMA': self._ema,
                'RSI': self._rsi,
                'MACD': self._macd,
                'BOLLINGER': self._bollinger_bands,
                'STOCHASTIC': self._stochastic,
                'ATR': self._atr
            })
        else:
            self.talib_available = False
            print("TA-Lib not available, using fallback implementations")
            # 注册备选指标实现
            self._indicators.update({
                'SMA': self._sma,
                'EMA': self._ema,
                'RSI': self._rsi,
                'MACD': self._macd,
                'BOLLINGER': self._bollinger_bands
            })

    def calculate(self, indicator_name: str, data: pd.Series, **params) -> Any:
        """
        计算指标
        """
        if indicator_name not in self._indicators:
            raise ValueError(f"Indicator {indicator_name} not supported")
        
        return self._indicators[indicator_name](data, **params)

    def _sma(self, data: pd.Series, period: int = 14) -> pd.Series:
        """简单移动平均"""
        return TalibAdapter.sma(data, period)

    def _ema(self, data: pd.Series, period: int = 14) -> pd.Series:
        """指数移动平均"""
        return TalibAdapter.ema(data, period)

    def _rsi(self, data: pd.Series, period: int = 14) -> pd.Series:
        """相对强弱指标"""
        return TalibAdapter.rsi(data, period)

    def _macd(self, data: pd.Series, fastperiod: int = 12, slowperiod: int = 26, signalperiod: int = 9) -> Dict[str, pd.Series]:
        """移动平均收敛发散指标"""
        return TalibAdapter.macd(data, fastperiod, slowperiod, signalperiod)

    def _bollinger_bands(self, data: pd.Series, period: int = 20, nbdevup: int = 2, nbdevdn: int = 2) -> Dict[str, pd.Series]:
        """布林带"""
        return TalibAdapter.bollinger_bands(data, period, nbdevup, nbdevdn)

    def _stochastic(self, high: pd.Series, low: pd.Series, close: pd.Series, 
                    fastk_period: int = 5, slowk_period: int = 3, slowd_period: int = 3) -> Dict[str, pd.Series]:
        """随机指标"""
        return TalibAdapter.stochastic(high, low, close, fastk_period, slowk_period, slowd_period)

    def _atr(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """平均真实波幅"""
        if not self.talib_available:
            # 简单的ATR实现
            import numpy as np
            high_low = high - low
            high_close = np.abs(high - close.shift())
            low_close = np.abs(low - close.shift())
            ranges = pd.concat([high_low, high_close, low_close], axis=1)
            true_range = ranges.max(axis=1)
            return true_range.rolling(window=period).mean()
        import talib
        return pd.Series(talib.ATR(high.values, low.values, close.values, timeperiod=period), 
                         index=close.index)

    def get_available_indicators(self) -> List[str]:
        """获取可用指标列表"""
        return list(self._indicators.keys())