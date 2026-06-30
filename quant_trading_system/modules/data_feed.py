"""
行情数据订阅模块
支持多种数据源：Binance WebSocket、CSV文件、QMT/通达信API
"""

import asyncio
import websocket
import json
import threading
import time
from datetime import datetime
from typing import Dict, List, Callable, Optional
import pandas as pd
import requests
import yaml
import os
from queue import Queue

from ..database.sqlite_manager import SQLiteManager
from ..models.market_data import MarketData, MarketDataProcessor


class BaseDataFeed:
    """基础数据源类"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """初始化数据源"""
        self.config = self._load_config(config_path)
        self.db_manager = SQLiteManager(self.config['database']['sqlite_path'])
        self.data_queue = Queue()
        self.running = False
        self.callbacks = []
    
    def _load_config(self, config_path: str) -> Dict:
        """加载配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"配置文件 {config_path} 不存在，使用默认配置")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """获取默认配置"""
        return {
            'database': {'sqlite_path': './data/trading.db'},
            'data_source': {
                'binance': {
                    'api_key': '',
                    'api_secret': '',
                    'symbols': ['BTCUSDT'],
                    'update_interval': 1
                }
            }
        }
    
    def register_callback(self, callback: Callable):
        """注册数据回调函数"""
        self.callbacks.append(callback)
    
    def start(self):
        """启动数据订阅"""
        raise NotImplementedError
    
    def stop(self):
        """停止数据订阅"""
        self.running = False
    
    def get_historical_data(self, symbol: str, start_time: datetime, 
                           end_time: datetime, timeframe: str = "1m") -> pd.DataFrame:
        """获取历史数据"""
        raise NotImplementedError


class BinanceWebSocketFeed(BaseDataFeed):
    """币安WebSocket数据源"""
    
    def __init__(self, config_path: str = "config.yaml"):
        super().__init__(config_path)
        self.ws = None
        self.symbols = self.config['data_source']['binance']['symbols']
        self.ws_url = "wss://stream.binance.com:9443/ws"
        self.rest_url = "https://api.binance.com/api/v3"
        
        # 如果是测试网
        if self.config['data_source']['binance'].get('testnet', False):
            self.ws_url = "wss://testnet.binance.vision/ws"
            self.rest_url = "https://testnet.binance.vision/api/v3"
    
    def _create_stream_names(self) -> List[str]:
        """创建WebSocket流名称"""
        streams = []
        for symbol in self.symbols:
            streams.append(f"{symbol.lower()}@kline_1m")
            streams.append(f"{symbol.lower()}@kline_5m")
            streams.append(f"{symbol.lower()}@kline_1h")
        return streams
    
    def _on_message(self, ws, message):
        """WebSocket消息处理"""
        try:
            data = json.loads(message)
            
            # 处理K线数据
            if 'k' in data:
                kline = data['k']
                symbol = kline['s']
                
                market_data = MarketData(
                    symbol=symbol,
                    timestamp=datetime.fromtimestamp(kline['t'] / 1000),
                    open=float(kline['o']),
                    high=float(kline['h']),
                    low=float(kline['l']),
                    close=float(kline['c']),
                    volume=float(kline['v']),
                    quote_volume=float(kline['q']),
                    trades=kline['n'],
                    timeframe=kline['i']
                )
                
                # 保存到数据库
                self.db_manager.save_market_data(
                    symbol=market_data.symbol,
                    timestamp=market_data.timestamp,
                    open_price=market_data.open,
                    high=market_data.high,
                    low=market_data.low,
                    close=market_data.close,
                    volume=market_data.volume,
                    timeframe=market_data.timeframe,
                    quote_volume=market_data.quote_volume,
                    trades=market_data.trades
                )
                
                # 放入队列
                self.data_queue.put(market_data)
                
                # 调用回调函数
                for callback in self.callbacks:
                    callback(market_data)
                
                # 打印日志
                print(f"[{datetime.now()}] {symbol} {market_data.timeframe}: {market_data.close}")
        
        except Exception as e:
            print(f"处理WebSocket消息失败: {e}")
    
    def _on_error(self, ws, error):
        """WebSocket错误处理"""
        print(f"WebSocket错误: {error}")
    
    def _on_close(self, ws, close_status_code, close_msg):
        """WebSocket关闭处理"""
        print(f"WebSocket连接关闭: {close_status_code} - {close_msg}")
        if self.running:
            print("尝试重新连接...")
            time.sleep(5)
            self.start()
    
    def _on_open(self, ws):
        """WebSocket打开处理"""
        print("WebSocket连接已建立")
        
        # 订阅流
        streams = self._create_stream_names()
        subscription = {
            "method": "SUBSCRIBE",
            "params": streams,
            "id": 1
        }
        ws.send(json.dumps(subscription))
    
    def start(self):
        """启动WebSocket连接"""
        self.running = True
        
        # 创建WebSocket连接
        self.ws = websocket.WebSocketApp(
            self.ws_url,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close
        )
        
        # 在单独线程中运行
        self.ws_thread = threading.Thread(target=self.ws.run_forever)
        self.ws_thread.daemon = True
        self.ws_thread.start()
        
        print(f"币安WebSocket数据源已启动，订阅交易对: {self.symbols}")
    
    def get_historical_data(self, symbol: str, start_time: datetime, 
                           end_time: datetime, timeframe: str = "1m") -> pd.DataFrame:
        """从币安API获取历史数据"""
        
        # 时间间隔映射
        interval_map = {
            '1m': '1m',
            '5m': '5m',
            '15m': '15m',
            '1h': '1h',
            '4h': '4h',
            '1d': '1d'
        }
        
        if timeframe not in interval_map:
            raise ValueError(f"不支持的时间周期: {timeframe}")
        
        interval = interval_map[timeframe]
        
        # 计算开始和结束时间戳
        start_ts = int(start_time.timestamp() * 1000)
        end_ts = int(end_time.timestamp() * 1000)
        
        all_data = []
        current_start = start_ts
        
        # 每次最多获取1000条数据
        while current_start < end_ts:
            params = {
                'symbol': symbol,
                'interval': interval,
                'startTime': current_start,
                'endTime': min(current_start + 1000 * 60 * 1000, end_ts),  # 1000根K线
                'limit': 1000
            }
            
            try:
                response = requests.get(f"{self.rest_url}/klines", params=params)
                response.raise_for_status()
                data = response.json()
                
                if not data:
                    break
                
                for item in data:
                    kline_data = {
                        'timestamp': datetime.fromtimestamp(item[0] / 1000),
                        'open': float(item[1]),
                        'high': float(item[2]),
                        'low': float(item[3]),
                        'close': float(item[4]),
                        'volume': float(item[5]),
                        'close_time': datetime.fromtimestamp(item[6] / 1000),
                        'quote_volume': float(item[7]),
                        'trades': int(item[8]),
                        'taker_buy_base': float(item[9]),
                        'taker_buy_quote': float(item[10]),
                        'timeframe': timeframe
                    }
                    all_data.append(kline_data)
                
                # 更新起始时间
                current_start = int(data[-1][0]) + 1
                
                # 避免请求频率限制
                time.sleep(0.1)
                
            except requests.exceptions.RequestException as e:
                print(f"获取历史数据失败: {e}")
                break
        
        # 转换为DataFrame
        if all_data:
            df = pd.DataFrame(all_data)
            df.set_index('timestamp', inplace=True)
            return df
        
        return pd.DataFrame()


class CSVDataFeed(BaseDataFeed):
    """CSV文件数据源"""
    
    def __init__(self, config_path: str = "config.yaml"):
        super().__init__(config_path)
        self.data_path = self.config['data_source']['csv_data']['path']
        self.date_format = self.config['data_source']['csv_data']['date_format']
    
    def start(self):
        """启动CSV数据源（模拟实时数据）"""
        self.running = True
        print("CSV数据源已启动（模拟模式）")
    
    def get_historical_data(self, symbol: str, start_time: datetime, 
                           end_time: datetime, timeframe: str = "1m") -> pd.DataFrame:
        """从CSV文件读取历史数据"""
        csv_file = os.path.join(self.data_path, f"{symbol}_{timeframe}.csv")
        
        if not os.path.exists(csv_file):
            print(f"CSV文件不存在: {csv_file}")
            return pd.DataFrame()
        
        try:
            df = pd.read_csv(csv_file)
            
            # 解析时间戳
            df['timestamp'] = pd.to_datetime(df['timestamp'], format=self.date_format)
            df.set_index('timestamp', inplace=True)
            
            # 过滤时间范围
            mask = (df.index >= start_time) & (df.index <= end_time)
            filtered_df = df[mask].copy()
            
            # 处理数据
            processor = MarketDataProcessor()
            cleaned_df = processor.clean_data(filtered_df)
            
            return cleaned_df
            
        except Exception as e:
            print(f"读取CSV文件失败: {e}")
            return pd.DataFrame()


class MockDataFeed(BaseDataFeed):
    """模拟数据源（用于测试）"""
    
    def __init__(self, config_path: str = "config.yaml"):
        super().__init__(config_path)
        self.current_price = 100.0
        self.volatility = 0.01
        self.symbols = ['MOCKUSDT']
    
    def _generate_mock_data(self) -> MarketData:
        """生成模拟市场数据"""
        import random
        
        # 随机价格变动
        change = (random.random() - 0.5) * 2 * self.volatility * self.current_price
        new_price = self.current_price + change
        
        # 生成K线数据
        open_price = self.current_price
        close_price = new_price
        high_price = max(open_price, close_price) * (1 + random.random() * 0.005)
        low_price = min(open_price, close_price) * (1 - random.random() * 0.005)
        
        # 更新当前价格
        self.current_price = close_price
        
        return MarketData(
            symbol='MOCKUSDT',
            timestamp=datetime.now(),
            open=open_price,
            high=high_price,
            low=low_price,
            close=close_price,
            volume=random.random() * 1000,
            timeframe='1m'
        )
    
    def start(self):
        """启动模拟数据源"""
        self.running = True
        
        def _generate_loop():
            while self.running:
                market_data = self._generate_mock_data()
                
                # 保存到数据库
                self.db_manager.save_market_data(
                    symbol=market_data.symbol,
                    timestamp=market_data.timestamp,
                    open_price=market_data.open,
                    high=market_data.high,
                    low=market_data.low,
                    close=market_data.close,
                    volume=market_data.volume,
                    timeframe=market_data.timeframe
                )
                
                # 放入队列
                self.data_queue.put(market_data)
                
                # 调用回调函数
                for callback in self.callbacks:
                    callback(market_data)
                
                # 等待
                time.sleep(self.config['data_source']['binance']['update_interval'])
        
        # 启动生成线程
        self.mock_thread = threading.Thread(target=_generate_loop)
        self.mock_thread.daemon = True
        self.mock_thread.start()
        
        print("模拟数据源已启动")
    
    def get_historical_data(self, symbol: str, start_time: datetime, 
                           end_time: datetime, timeframe: str = "1m") -> pd.DataFrame:
        """生成模拟历史数据"""
        import random
        
        # 生成时间序列
        freq_map = {'1m': '1T', '5m': '5T', '1h': '1H', '1d': '1D'}
        freq = freq_map.get(timeframe, '1T')
        
        dates = pd.date_range(start=start_time, end=end_time, freq=freq)
        
        if len(dates) == 0:
            return pd.DataFrame()
        
        # 生成价格序列（几何布朗运动）
        base_price = 100.0
        mu = 0.0001  # 每日漂移率
        sigma = 0.01  # 每日波动率
        
        # 计算每个时间步
        dt = 1 / (len(dates) - 1) if len(dates) > 1 else 1
        prices = [base_price]
        
        for i in range(1, len(dates)):
            # 几何布朗运动
            drift = (mu - 0.5 * sigma**2) * dt
            shock = sigma * np.random.normal() * np.sqrt(dt)
            new_price = prices[-1] * np.exp(drift + shock)
            prices.append(new_price)
        
        # 创建DataFrame
        df = pd.DataFrame({
            'timestamp': dates,
            'open': [p * (1 - random.random() * 0.002) for p in prices],
            'high': [p * (1 + random.random() * 0.005) for p in prices],
            'low': [p * (1 - random.random() * 0.005) for p in prices],
            'close': prices,
            'volume': [random.random() * 1000 for _ in range(len(prices))],
            'timeframe': timeframe
        })
        
        df.set_index('timestamp', inplace=True)
        return df


class DataFeedFactory:
    """数据源工厂"""
    
    @staticmethod
    def create_feed(feed_type: str, config_path: str = "config.yaml") -> BaseDataFeed:
        """创建数据源实例"""
        if feed_type == "binance":
            return BinanceWebSocketFeed(config_path)
        elif feed_type == "csv":
            return CSVDataFeed(config_path)
        elif feed_type == "mock":
            return MockDataFeed(config_path)
        else:
            raise ValueError(f"不支持的数据源类型: {feed_type}")


if __name__ == "__main__":
    # 测试代码
    feed = DataFeedFactory.create_feed("mock", "config.yaml")
    
    def on_data(data):
        print(f"收到数据: {data.symbol} {data.close}")
    
    feed.register_callback(on_data)
    feed.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        feed.stop()
        print("数据源已停止")