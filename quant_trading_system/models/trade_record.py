"""
交易记录模型
定义交易记录数据结构和相关操作
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum
import pandas as pd
import numpy as np


class OrderSide(Enum):
    """订单方向枚举"""
    BUY = "BUY"
    SELL = "SELL"


class OrderType(Enum):
    """订单类型枚举"""
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"
    STOP_LIMIT = "STOP_LIMIT"


class OrderStatus(Enum):
    """订单状态枚举"""
    OPEN = "OPEN"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"


@dataclass
class TradeRecord:
    """交易记录类"""
    trade_id: str
    symbol: str
    side: OrderSide
    price: float
    quantity: float
    fee: float
    order_type: OrderType
    status: OrderStatus
    timestamp: datetime
    filled_time: Optional[datetime] = None
    realized_pnl: float = 0.0
    commission_asset: str = "USDT"
    client_order_id: Optional[str] = None
    strategy_name: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'trade_id': self.trade_id,
            'symbol': self.symbol,
            'side': self.side.value,
            'price': self.price,
            'quantity': self.quantity,
            'fee': self.fee,
            'realized_pnl': self.realized_pnl,
            'order_type': self.order_type.value,
            'status': self.status.value,
            'timestamp': self.timestamp,
            'filled_time': self.filled_time,
            'commission_asset': self.commission_asset,
            'client_order_id': self.client_order_id,
            'strategy_name': self.strategy_name
        }
    
    def calculate_value(self) -> float:
        """计算交易价值"""
        return self.price * self.quantity
    
    def calculate_fee_value(self) -> float:
        """计算手续费价值"""
        return self.fee * self.price if self.commission_asset == self.symbol.split('USDT')[0] else self.fee


class TradeAnalyzer:
    """交易分析器"""
    
    @staticmethod
    def analyze_trades(trades: List[TradeRecord]) -> Dict:
        """
        分析交易记录
        
        Args:
            trades: 交易记录列表
            
        Returns:
            分析结果字典
        """
        if not trades:
            return {}
        
        # 转换为DataFrame
        df = pd.DataFrame([trade.to_dict() for trade in trades])
        
        # 基本统计
        total_trades = len(df)
        profitable_trades = len(df[df['realized_pnl'] > 0])
        losing_trades = len(df[df['realized_pnl'] < 0])
        
        # 按方向统计
        buy_trades = len(df[df['side'] == OrderSide.BUY.value])
        sell_trades = len(df[df['side'] == OrderSide.SELL.value])
        
        # 盈亏统计
        total_pnl = df['realized_pnl'].sum()
        avg_pnl = df['realized_pnl'].mean()
        max_win = df['realized_pnl'].max()
        max_loss = df['realized_pnl'].min()
        
        # 手续费统计
        total_fee = df['fee'].sum()
        
        # 胜率
        win_rate = profitable_trades / total_trades if total_trades > 0 else 0
        
        # 盈亏比
        avg_win = df[df['realized_pnl'] > 0]['realized_pnl'].mean() if profitable_trades > 0 else 0
        avg_loss = abs(df[df['realized_pnl'] < 0]['realized_pnl'].mean()) if losing_trades > 0 else 0
        profit_loss_ratio = avg_win / avg_loss if avg_loss > 0 else float('inf')
        
        # 按时间分析
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['date'] = df['timestamp'].dt.date
            daily_pnl = df.groupby('date')['realized_pnl'].sum()
            
            # 连续盈亏
            pnl_series = df.sort_values('timestamp')['realized_pnl'].values
            max_consecutive_wins = TradeAnalyzer._max_consecutive(pnl_series, positive=True)
            max_consecutive_losses = TradeAnalyzer._max_consecutive(pnl_series, positive=False)
        
        return {
            'total_trades': total_trades,
            'profitable_trades': profitable_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'avg_pnl': avg_pnl,
            'max_win': max_win,
            'max_loss': max_loss,
            'buy_trades': buy_trades,
            'sell_trades': sell_trades,
            'total_fee': total_fee,
            'profit_loss_ratio': profit_loss_ratio,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'max_consecutive_wins': max_consecutive_wins if 'max_consecutive_wins' in locals() else 0,
            'max_consecutive_losses': max_consecutive_losses if 'max_consecutive_losses' in locals() else 0,
            'daily_pnl_stats': {
                'mean': daily_pnl.mean() if 'daily_pnl' in locals() else 0,
                'std': daily_pnl.std() if 'daily_pnl' in locals() else 0,
                'max': daily_pnl.max() if 'daily_pnl' in locals() else 0,
                'min': daily_pnl.min() if 'daily_pnl' in locals() else 0
            } if 'daily_pnl' in locals() else {}
        }
    
    @staticmethod
    def _max_consecutive(series: np.ndarray, positive: bool = True) -> int:
        """计算最大连续次数"""
        if positive:
            condition = series > 0
        else:
            condition = series < 0
        
        max_count = 0
        current_count = 0
        
        for value in condition:
            if value:
                current_count += 1
                max_count = max(max_count, current_count)
            else:
                current_count = 0
        
        return max_count
    
    @staticmethod
    def calculate_drawdown(pnl_series: pd.Series) -> Dict:
        """
        计算回撤
        
        Args:
            pnl_series: 盈亏时间序列
            
        Returns:
            回撤统计
        """
        if pnl_series.empty:
            return {}
        
        # 计算累计收益
        cumulative = pnl_series.cumsum()
        
        # 计算回撤
        running_max = cumulative.expanding().max()
        drawdown = cumulative - running_max
        
        # 最大回撤
        max_drawdown = drawdown.min()
        max_drawdown_period = drawdown.idxmin() if not drawdown.empty else None
        
        # 恢复时间
        recovery_info = {}
        if max_drawdown_period and not drawdown.empty:
            # 寻找恢复到前高之前的时间
            post_drawdown = drawdown[max_drawdown_period:]
            recovery_idx = post_drawdown[post_drawdown >= 0].first_valid_index()
            if recovery_idx:
                recovery_time = (recovery_idx - max_drawdown_period).total_seconds() / 3600  # 小时
                recovery_info = {
                    'recovery_time_hours': recovery_time,
                    'recovery_date': recovery_idx
                }
        
        return {
            'max_drawdown': max_drawdown,
            'max_drawdown_date': max_drawdown_period,
            'current_drawdown': drawdown.iloc[-1] if not drawdown.empty else 0,
            'recovery_info': recovery_info
        }
    
    @staticmethod
    def analyze_by_symbol(trades: List[TradeRecord]) -> Dict[str, Dict]:
        """
        按交易对分析
        
        Args:
            trades: 交易记录列表
            
        Returns:
            按交易对分组的分析结果
        """
        if not trades:
            return {}
        
        df = pd.DataFrame([trade.to_dict() for trade in trades])
        
        # 按symbol分组
        grouped = df.groupby('symbol')
        
        results = {}
        for symbol, group in grouped:
            analysis = TradeAnalyzer.analyze_trades([
                TradeRecord(**row.to_dict()) for _, row in group.iterrows()
            ])
            results[symbol] = analysis
        
        return results
    
    @staticmethod
    def analyze_by_strategy(trades: List[TradeRecord]) -> Dict[str, Dict]:
        """
        按策略分析
        
        Args:
            trades: 交易记录列表
            
        Returns:
            按策略分组的分析结果
        """
        if not trades:
            return {}
        
        df = pd.DataFrame([trade.to_dict() for trade in trades])
        
        # 按策略分组
        if 'strategy_name' in df.columns:
            grouped = df.groupby('strategy_name')
            
            results = {}
            for strategy, group in grouped:
                analysis = TradeAnalyzer.analyze_trades([
                    TradeRecord(**row.to_dict()) for _, row in group.iterrows()
                ])
                results[strategy] = analysis
            return results
        
        return {}


class TradeFilter:
    """交易过滤器"""
    
    @staticmethod
    def filter_by_timeframe(trades: List[TradeRecord], 
                           start_time: datetime, 
                           end_time: datetime) -> List[TradeRecord]:
        """按时间过滤"""
        return [t for t in trades if start_time <= t.timestamp <= end_time]
    
    @staticmethod
    def filter_by_symbol(trades: List[TradeRecord], symbol: str) -> List[TradeRecord]:
        """按交易对过滤"""
        return [t for t in trades if t.symbol == symbol]
    
    @staticmethod
    def filter_by_side(trades: List[TradeRecord], side: OrderSide) -> List[TradeRecord]:
        """按方向过滤"""
        return [t for t in trades if t.side == side]
    
    @staticmethod
    def filter_by_status(trades: List[TradeRecord], status: OrderStatus) -> List[TradeRecord]:
        """按状态过滤"""
        return [t for t in trades if t.status == status]
    
    @staticmethod
    def filter_profitable(trades: List[TradeRecord]) -> List[TradeRecord]:
        """筛选盈利交易"""
        return [t for t in trades if t.realized_pnl > 0]
    
    @staticmethod
    def filter_losing(trades: List[TradeRecord]) -> List[TradeRecord]:
        """筛选亏损交易"""
        return [t for t in trades if t.realized_pnl < 0]