import pandas as pd
import numpy as np
from typing import Dict, Any, Union

try:
    import talib
    TALIB_AVAILABLE = True
except ImportError:
    TALIB_AVAILABLE = False
    print("TA-Lib not available. Please install it with: pip install TA-Lib")

class TalibAdapter:
    """
    TA-Lib适配器，提供对TA-Lib库的封装
    """
    
    @staticmethod
    def is_available() -> bool:
        """
        检查TA-Lib是否可用
        """
        return TALIB_AVAILABLE
    
    @staticmethod
    def sma(data: pd.Series, period: int = 30) -> pd.Series:
        """
        计算简单移动平均线
        """
        if not TALIB_AVAILABLE:
            # 如果TA-Lib不可用，使用pandas作为备选方案
            return data.rolling(window=period).mean()
        
        result = talib.SMA(data.values, timeperiod=period)
        return pd.Series(result, index=data.index)
    
    @staticmethod
    def ema(data: pd.Series, period: int = 30) -> pd.Series:
        """
        计算指数移动平均线
        """
        if not TALIB_AVAILABLE:
            # 如果TA-Lib不可用，使用pandas作为备选方案
            return data.ewm(span=period).mean()
        
        result = talib.EMA(data.values, timeperiod=period)
        return pd.Series(result, index=data.index)
    
    @staticmethod
    def rsi(data: pd.Series, period: int = 14) -> pd.Series:
        """
        计算相对强弱指数
        """
        if not TALIB_AVAILABLE:
            # 如果TA-Lib不可用，使用简单的实现
            delta = data.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            return 100 - (100 / (1 + rs))
        
        result = talib.RSI(data.values, timeperiod=period)
        return pd.Series(result, index=data.index)
    
    @staticmethod
    def macd(data: pd.Series, fastperiod: int = 12, slowperiod: int = 26, signalperiod: int = 9) -> Dict[str, pd.Series]:
        """
        计算MACD指标
        """
        if not TALIB_AVAILABLE:
            # 如果TA-Lib不可用，使用简单的实现
            exp1 = data.ewm(span=fastperiod).mean()
            exp2 = data.ewm(span=slowperiod).mean()
            macd = exp1 - exp2
            signal = macd.ewm(span=signalperiod).mean()
            histogram = macd - signal
            return {
                "macd": macd,
                "signal": signal,
                "histogram": histogram
            }
        
        macd, macdsignal, macdhist = talib.MACD(
            data.values, 
            fastperiod=fastperiod, 
            slowperiod=slowperiod, 
            signalperiod=signalperiod
        )
        
        index = data.index
        return {
            "macd": pd.Series(macd, index=index),
            "signal": pd.Series(macdsignal, index=index),
            "histogram": pd.Series(macdhist, index=index)
        }
    
    @staticmethod
    def bollinger_bands(
        data: pd.Series, 
        period: int = 20, 
        nbdevup: int = 2, 
        nbdevdn: int = 2
    ) -> Dict[str, pd.Series]:
        """
        计算布林带
        """
        if not TALIB_AVAILABLE:
            # 如果TA-Lib不可用，使用简单的实现
            ma = data.rolling(window=period).mean()
            std = data.rolling(window=period).std()
            upper = ma + (std * nbdevup)
            lower = ma - (std * nbdevdn)
            return {
                "upper": upper,
                "middle": ma,
                "lower": lower
            }
        
        upper, middle, lower = talib.BBANDS(
            data.values,
            timeperiod=period,
            nbdevup=nbdevup,
            nbdevdn=nbdevdn,
            matype=0
        )
        
        index = data.index
        return {
            "upper": pd.Series(upper, index=index),
            "middle": pd.Series(middle, index=index),
            "lower": pd.Series(lower, index=index)
        }
    
    @staticmethod
    def stochastic(
        high: pd.Series, 
        low: pd.Series, 
        close: pd.Series, 
        fastk_period: int = 5, 
        slowk_period: int = 3, 
        slowd_period: int = 3
    ) -> Dict[str, pd.Series]:
        """
        计算随机指标
        """
        if not TALIB_AVAILABLE:
            # 如果TA-Lib不可用，使用简单的实现
            lowest_low = low.rolling(window=fastk_period).min()
            highest_high = high.rolling(window=fastk_period).max()
            k = 100 * ((close - lowest_low) / (highest_high - lowest_low))
            slow_k = k.rolling(window=slowk_period).mean()
            slow_d = slow_k.rolling(window=slowd_period).mean()
            return {
                "slowk": slow_k,
                "slowd": slow_d
            }
        
        slowk, slowd = talib.STOCH(
            high.values,
            low.values,
            close.values,
            fastk_period=fastk_period,
            slowk_period=slowk_period,
            slowd_period=slowd_period
        )
        
        index = close.index
        return {
            "slowk": pd.Series(slowk, index=index),
            "slowd": pd.Series(slowd, index=index)
        }