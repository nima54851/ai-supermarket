"""
SQLite数据库管理器
负责所有数据表的创建、查询、更新和删除操作
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import pandas as pd
import os
from pathlib import Path


class SQLiteManager:
    """SQLite数据库管理类"""
    
    def __init__(self, db_path: str = "./data/trading.db"):
        """
        初始化数据库管理器
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self._create_database()
    
    def _create_database(self):
        """创建数据库和数据表"""
        # 确保目录存在
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 1. 市场数据表
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS market_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                open REAL NOT NULL,
                high REAL NOT NULL,
                low REAL NOT NULL,
                close REAL NOT NULL,
                volume REAL NOT NULL,
                quote_volume REAL,
                trades INTEGER,
                timeframe TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(symbol, timestamp, timeframe)
            )
            """)
            
            # 2. 交易记录表
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS trade_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trade_id TEXT UNIQUE NOT NULL,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,  -- BUY/SELL
                price REAL NOT NULL,
                quantity REAL NOT NULL,
                fee REAL DEFAULT 0.0,
                realized_pnl REAL DEFAULT 0.0,
                order_type TEXT NOT NULL,  -- MARKET/LIMIT/STOP
                status TEXT NOT NULL,  -- OPEN/FILLED/CANCELLED
                timestamp DATETIME NOT NULL,
                filled_time DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # 3. 投资组合表
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS portfolio (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                total_value REAL NOT NULL,
                cash REAL NOT NULL,
                positions JSON,  -- JSON格式存储持仓
                daily_return REAL,
                cumulative_return REAL,
                max_drawdown REAL,
                sharpe_ratio REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # 4. 指标数据表
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS indicators (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                timeframe TEXT NOT NULL,
                macd REAL,
                macd_signal REAL,
                macd_histogram REAL,
                rsi REAL,
                bb_upper REAL,
                bb_middle REAL,
                bb_lower REAL,
                ma_5 REAL,
                ma_10 REAL,
                ma_20 REAL,
                ma_30 REAL,
                ma_60 REAL,
                volume_ma REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(symbol, timestamp, timeframe)
            )
            """)
            
            # 5. 随机漫步分析表
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS random_walk_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                log_return_mean REAL,
                log_return_std REAL,
                rolling_volatility REAL,
                hurst_exponent REAL,
                gbm_mu REAL,
                gbm_sigma REAL,
                residuals_mean REAL,
                residuals_std REAL,
                is_random_walk BOOLEAN,
                confidence_level REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # 6. 回测结果表
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS backtest_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                strategy_name TEXT NOT NULL,
                start_date DATETIME NOT NULL,
                end_date DATETIME NOT NULL,
                initial_capital REAL NOT NULL,
                final_value REAL NOT NULL,
                total_return REAL NOT NULL,
                annual_return REAL,
                sharpe_ratio REAL,
                max_drawdown REAL,
                win_rate REAL,
                total_trades INTEGER,
                profitable_trades INTEGER,
                parameters JSON,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # 创建索引
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_market_data_symbol_time ON market_data(symbol, timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_trade_records_symbol_time ON trade_records(symbol, timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_indicators_symbol_time ON indicators(symbol, timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_portfolio_time ON portfolio(timestamp)")
            
            conn.commit()
    
    def save_market_data(self, symbol: str, timestamp: datetime, 
                         open_price: float, high: float, low: float, 
                         close: float, volume: float, timeframe: str,
                         quote_volume: float = None, trades: int = None) -> bool:
        """
        保存市场数据
        
        Args:
            symbol: 交易对
            timestamp: 时间戳
            open_price: 开盘价
            high: 最高价
            low: 最低价
            close: 收盘价
            volume: 成交量
            timeframe: 时间周期
            quote_volume: 报价成交量
            trades: 交易笔数
            
        Returns:
            是否保存成功
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                INSERT OR REPLACE INTO market_data 
                (symbol, timestamp, open, high, low, close, volume, 
                 quote_volume, trades, timeframe)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (symbol, timestamp, open_price, high, low, close, 
                      volume, quote_volume, trades, timeframe))
                conn.commit()
                return True
        except Exception as e:
            print(f"保存市场数据失败: {e}")
            return False
    
    def save_trade_record(self, trade_id: str, symbol: str, side: str, 
                          price: float, quantity: float, fee: float,
                          order_type: str, status: str, timestamp: datetime,
                          realized_pnl: float = 0.0, filled_time: datetime = None) -> bool:
        """
        保存交易记录
        
        Args:
            trade_id: 交易ID
            symbol: 交易对
            side: 买卖方向
            price: 价格
            quantity: 数量
            fee: 手续费
            order_type: 订单类型
            status: 状态
            timestamp: 时间戳
            realized_pnl: 已实现盈亏
            filled_time: 成交时间
            
        Returns:
            是否保存成功
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                INSERT INTO trade_records 
                (trade_id, symbol, side, price, quantity, fee, realized_pnl, 
                 order_type, status, timestamp, filled_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (trade_id, symbol, side, price, quantity, fee, realized_pnl,
                      order_type, status, timestamp, filled_time))
                conn.commit()
                return True
        except Exception as e:
            print(f"保存交易记录失败: {e}")
            return False
    
    def get_trade_records(self, symbol: str = None, 
                          start_time: datetime = None, 
                          end_time: datetime = None,
                          limit: int = 100) -> pd.DataFrame:
        """
        获取交易记录
        
        Args:
            symbol: 交易对
            start_time: 开始时间
            end_time: 结束时间
            limit: 限制数量
            
        Returns:
            交易记录DataFrame
        """
        query = "SELECT * FROM trade_records WHERE 1=1"
        params = []
        
        if symbol:
            query += " AND symbol = ?"
            params.append(symbol)
        
        if start_time:
            query += " AND timestamp >= ?"
            params.append(start_time)
        
        if end_time:
            query += " AND timestamp <= ?"
            params.append(end_time)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                df = pd.read_sql_query(query, conn, params=tuple(params))
                return df
        except Exception as e:
            print(f"获取交易记录失败: {e}")
            return pd.DataFrame()
    
    def save_portfolio_snapshot(self, timestamp: datetime, total_value: float,
                                cash: float, positions: Dict, daily_return: float = None,
                                cumulative_return: float = None, max_drawdown: float = None,
                                sharpe_ratio: float = None) -> bool:
        """
        保存投资组合快照
        
        Args:
            timestamp: 时间戳
            total_value: 总资产
            cash: 现金
            positions: 持仓字典
            daily_return: 日收益率
            cumulative_return: 累计收益率
            max_drawdown: 最大回撤
            sharpe_ratio: 夏普比率
            
        Returns:
            是否保存成功
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                INSERT INTO portfolio 
                (timestamp, total_value, cash, positions, daily_return, 
                 cumulative_return, max_drawdown, sharpe_ratio)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (timestamp, total_value, cash, json.dumps(positions), 
                      daily_return, cumulative_return, max_drawdown, sharpe_ratio))
                conn.commit()
                return True
        except Exception as e:
            print(f"保存投资组合快照失败: {e}")
            return False
    
    def get_portfolio_history(self, start_time: datetime = None,
                              end_time: datetime = None) -> pd.DataFrame:
        """
        获取投资组合历史
        
        Args:
            start_time: 开始时间
            end_time: 结束时间
            
        Returns:
            投资组合历史DataFrame
        """
        query = "SELECT * FROM portfolio WHERE 1=1"
        params = []
        
        if start_time:
            query += " AND timestamp >= ?"
            params.append(start_time)
        
        if end_time:
            query += " AND timestamp <= ?"
            params.append(end_time)
        
        query += " ORDER BY timestamp ASC"
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                df = pd.read_sql_query(query, conn, params=tuple(params))
                if not df.empty and 'positions' in df.columns:
                    # 解析JSON格式的持仓
                    df['positions'] = df['positions'].apply(lambda x: json.loads(x) if pd.notna(x) else {})
                return df
        except Exception as e:
            print(f"获取投资组合历史失败: {e}")
            return pd.DataFrame()
    
    def save_indicators(self, symbol: str, timestamp: datetime, timeframe: str,
                        indicators_dict: Dict[str, float]) -> bool:
        """
        保存技术指标
        
        Args:
            symbol: 交易对
            timestamp: 时间戳
            timeframe: 时间周期
            indicators_dict: 指标字典
            
        Returns:
            是否保存成功
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                INSERT OR REPLACE INTO indicators 
                (symbol, timestamp, timeframe, macd, macd_signal, macd_histogram, 
                 rsi, bb_upper, bb_middle, bb_lower, ma_5, ma_10, ma_20, ma_30, ma_60, volume_ma)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    symbol, timestamp, timeframe,
                    indicators_dict.get('macd'),
                    indicators_dict.get('macd_signal'),
                    indicators_dict.get('macd_histogram'),
                    indicators_dict.get('rsi'),
                    indicators_dict.get('bb_upper'),
                    indicators_dict.get('bb_middle'),
                    indicators_dict.get('bb_lower'),
                    indicators_dict.get('ma_5'),
                    indicators_dict.get('ma_10'),
                    indicators_dict.get('ma_20'),
                    indicators_dict.get('ma_30'),
                    indicators_dict.get('ma_60'),
                    indicators_dict.get('volume_ma')
                ))
                conn.commit()
                return True
        except Exception as e:
            print(f"保存技术指标失败: {e}")
            return False
    
    def backup_database(self, backup_path: str = None) -> bool:
        """
        备份数据库
        
        Args:
            backup_path: 备份路径
            
        Returns:
            是否备份成功
        """
        if backup_path is None:
            backup_path = f"{self.db_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            # 使用SQLite的备份API
            source_conn = sqlite3.connect(self.db_path)
            backup_conn = sqlite3.connect(backup_path)
            
            source_conn.backup(backup_conn)
            
            source_conn.close()
            backup_conn.close()
            
            print(f"数据库备份成功: {backup_path}")
            return True
        except Exception as e:
            print(f"数据库备份失败: {e}")
            return False
    
    def get_market_data(self, symbol: str, timeframe: str,
                        start_time: datetime = None,
                        end_time: datetime = None,
                        limit: int = 1000) -> pd.DataFrame:
        """
        获取市场数据
        
        Args:
            symbol: 交易对
            timeframe: 时间周期
            start_time: 开始时间
            end_time: 结束时间
            limit: 限制数量
            
        Returns:
            市场数据DataFrame
        """
        query = "SELECT * FROM market_data WHERE symbol = ? AND timeframe = ?"
        params = [symbol, timeframe]
        
        if start_time:
            query += " AND timestamp >= ?"
            params.append(start_time)
        
        if end_time:
            query += " AND timestamp <= ?"
            params.append(end_time)
        
        query += " ORDER BY timestamp ASC LIMIT ?"
        params.append(limit)
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                df = pd.read_sql_query(query, conn, params=tuple(params))
                return df
        except Exception as e:
            print(f"获取市场数据失败: {e}")
            return pd.DataFrame()
    
    def __del__(self):
        """析构函数"""
        pass