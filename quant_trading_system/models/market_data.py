"""
市场数据模型
定义行情数据结构和相关操作
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd
import numpy as np


@dataclass
class MarketData:
    """市场数据类"""
    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    quote_volume: Optional[float] = None
    trades: Optional[int] = None
    timeframe: str = "1m"
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'symbol': self.symbol,
            'timestamp': self.timestamp,
            'open': self.open,
            'high': self.high,
            'low': self.low,
            'close': self.close,
            'volume': self.volume,
            'quote_volume': self.quote_volume,
            'trades': self.trades,
            'timeframe': self.timeframe
        }


class MarketDataProcessor:
    """市场数据处理器"""
    
    @staticmethod
    def resample_data(df: pd.DataFrame, timeframe: str) -> pd.DataFrame:
        """
        重新采样数据
        
        Args:
            df: 原始数据DataFrame
            timeframe: 目标时间周期
            
        Returns:
            重采样后的DataFrame
        """
        if df.empty:
            return df
        
        # 确保时间戳是DatetimeIndex
        df = df.copy()
        if not isinstance(df.index, pd.DatetimeIndex):
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df.set_index('timestamp', inplace=True)
        
        # 重采样规则
        rules = {
            '1m': '1T',
            '5m': '5T',
            '15m': '15T',
            '1h': '1H',
            '4h': '4H',
            '1d': '1D'
        }
        
        if timeframe not in rules:
            raise ValueError(f"不支持的时间周期: {timeframe}")
        
        rule = rules[timeframe]
        
        # 使用ohlc方法重采样
        resampled = df.resample(rule).agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum',
            'quote_volume': 'sum' if 'quote_volume' in df.columns else None,
            'trades': 'sum' if 'trades' in df.columns else None
        }).dropna()
        
        return resampled
    
    @staticmethod
    def calculate_returns(df: pd.DataFrame) -> pd.DataFrame:
        """
        计算收益率
        
        Args:
            df: 价格数据DataFrame
            
        Returns:
            包含收益率的DataFrame
        """
        if df.empty:
            return df
        
        df = df.copy()
        
        # 简单收益率
        df['simple_return'] = df['close'].pct_change()
        
        # 对数收益率 (用于随机漫步分析)
        df['log_return'] = np.log(df['close'] / df['close'].shift(1))
        
        # 滚动收益率统计
        window = min(20, len(df))  # 使用较小窗口
        if window > 1:
            df['rolling_return_mean'] = df['simple_return'].rolling(window=window).mean()
            df['rolling_return_std'] = df['simple_return'].rolling(window=window).std()
        
        return df
    
    @staticmethod
    def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """
        计算技术指标
        
        Args:
            df: 价格数据DataFrame
            
        Returns:
            包含技术指标的DataFrame
        """
        if df.empty:
            return df
        
        df = df.copy()
        
        # 移动平均线
        periods = [5, 10, 20, 30, 60]
        for period in periods:
            df[f'ma_{period}'] = df['close'].rolling(window=period).mean()
        
        # 计算标准差
        df['std_20'] = df['close'].rolling(window=20).std()
        
        # 布林带
        df['bb_middle'] = df['ma_20']
        df['bb_upper'] = df['bb_middle'] + 2 * df['std_20']
        df['bb_lower'] = df['bb_middle'] - 2 * df['std_20']
        
        # RSI计算
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD计算
        exp1 = df['close'].ewm(span=12, adjust=False).mean()
        exp2 = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = exp1 - exp2
        df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        df['macd_histogram'] = df['macd'] - df['macd_signal']
        
        # 成交量移动平均
        df['volume_ma'] = df['volume'].rolling(window=20).mean()
        
        return df
    
    @staticmethod
    def detect_anomalies(df: pd.DataFrame, threshold: float = 3.0) -> pd.DataFrame:
        """
        检测数据异常
        
        Args:
            df: 价格数据DataFrame
            threshold: Z-score阈值
            
        Returns:
            包含异常标记的DataFrame
        """
        if df.empty:
            return df
        
        df = df.copy()
        
        # 计算价格变化的Z-score
        price_changes = df['close'].pct_change()
        z_scores = (price_changes - price_changes.mean()) / price_changes.std()
        
        # 标记异常
        df['is_anomaly'] = np.abs(z_scores) > threshold
        
        # 异常类型
        df['anomaly_type'] = 'normal'
        df.loc[(z_scores > threshold), 'anomaly_type'] = 'spike_up'
        df.loc[(z_scores < -threshold), 'anomaly_type'] = 'spike_down'
        
        return df
    
    @staticmethod
    def clean_data(df: pd.DataFrame) -> pd.DataFrame:
        """
        数据清洗
        
        Args:
            df: 原始数据DataFrame
            
        Returns:
            清洗后的DataFrame
        """
        if df.empty:
            return df
        
        df = df.copy()
        
        # 1. 处理缺失值
        df = df.dropna()
        
        # 2. 移除重复数据
        df = df.drop_duplicates()
        
        # 3. 检查价格合理性
        df = df[(df['high'] >= df['low']) & 
                (df['high'] >= df['open']) & 
                (df['high'] >= df['close']) &
                (df['low'] <= df['open']) & 
                (df['low'] <= df['close'])]
        
        # 4. 移除异常大的价格变动 (超过50%)
        price_changes = df['close'].pct_change().abs()
        df = df[price_changes <= 0.5]
        
        # 5. 确保时间顺序
        df = df.sort_index()
        
        return df
    
    @staticmethod
    def calculate_statistics(df: pd.DataFrame) -> Dict:
        """
        计算统计指标
        
        Args:
            df: 价格数据DataFrame
            
        Returns:
            统计指标字典
        """
        if df.empty:
            return {}
        
        stats = {}
        
        # 基本统计
        stats['mean_price'] = df['close'].mean()
        stats['std_price'] = df['close'].std()
        stats['min_price'] = df['close'].min()
        stats['max_price'] = df['close'].max()
        
        # 收益率统计
        returns = df['close'].pct_change().dropna()
        if len(returns) > 0:
            stats['mean_return'] = returns.mean()
            stats['std_return'] = returns.std()
            stats['sharpe_ratio'] = (returns.mean() / returns.std()) * np.sqrt(252) if returns.std() > 0 else 0
        
        # 成交量统计
        stats['mean_volume'] = df['volume'].mean()
        stats['max_volume'] = df['volume'].max()
        stats['volume_ratio'] = df['volume'].iloc[-1] / stats['mean_volume'] if stats['mean_volume'] > 0 else 0
        
        # 价格相关性 (如果有多个交易对)
        if 'symbol' in df.columns and df['symbol'].nunique() > 1:
            pivot = df.pivot(columns='symbol', values='close')
            correlation_matrix = pivot.corr()
            stats['correlation_matrix'] = correlation_matrix
        
        return stats