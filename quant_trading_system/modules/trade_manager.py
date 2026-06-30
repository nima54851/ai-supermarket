"""
交易管理模块
处理交易执行、记录和监控
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from queue import Queue
import threading
import time

from ..database.sqlite_manager import SQLiteManager
from ..models.trade_record import TradeRecord, OrderSide, OrderType, OrderStatus, TradeAnalyzer
from ..modules.risk_manager import RiskManager


class TradeManager:
    """交易管理器"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """初始化交易管理器"""
        self.config = self._load_config(config_path)
        self.db_manager = SQLiteManager(self.config['database']['sqlite_path'])
        self.risk_manager = RiskManager(config_path)
        
        # 交易队列
        self.trade_queue = Queue()
        self.pending_orders = {}  # 挂单字典
        self.filled_orders = {}   # 已成交订单
        
        # 账户状态
        self.account_balance = {
            'total_value': self.config.get('initial_capital', 10000.0),
            'cash': self.config.get('initial_capital', 10000.0),
            'positions': {},  # symbol: {'quantity': qty, 'avg_price': price}
            'unrealized_pnl': 0.0,
            'realized_pnl': 0.0
        }
        
        # 性能指标
        self.performance_metrics = {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'total_commission': 0.0,
            'sharpe_ratio': 0.0,
            'max_drawdown': 0.0,
            'current_drawdown': 0.0
        }
        
        # 线程控制
        self.running = False
        self.processing_thread = None
        
        # 交易记录
        self.trade_history = []
        
        # 最新市场价格
        self.latest_prices = {}
        
        print("交易管理器初始化完成")
    
    def _load_config(self, config_path: str) -> Dict:
        """加载配置文件"""
        import yaml
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
            'trading': {
                'risk': {
                    'max_position_pct': 0.3,
                    'max_loss_per_trade': 0.01,
                    'stop_loss_pct': 0.02,
                    'take_profit_pct': 0.05
                },
                'fee': {
                    'maker': 0.001,
                    'taker': 0.001
                },
                'min_qty': {
                    'BTCUSDT': 0.0001,
                    'ETHUSDT': 0.001
                }
            },
            'initial_capital': 10000.0
        }
    
    def update_market_price(self, symbol: str, price: float, timestamp: datetime = None):
        """更新市场价格"""
        self.latest_prices[symbol] = {
            'price': price,
            'timestamp': timestamp or datetime.now()
        }
        
        # 更新未实现盈亏
        self._update_unrealized_pnl()
    
    def _update_unrealized_pnl(self):
        """更新未实现盈亏"""
        total_unrealized = 0.0
        
        for symbol, position in self.account_balance['positions'].items():
            if symbol in self.latest_prices:
                current_price = self.latest_prices[symbol]['price']
                avg_price = position['avg_price']
                quantity = position['quantity']
                
                # 计算未实现盈亏
                if position['direction'] == 'LONG':
                    unrealized = (current_price - avg_price) * quantity
                else:  # SHORT
                    unrealized = (avg_price - current_price) * quantity
                
                total_unrealized += unrealized
        
        self.account_balance['unrealized_pnl'] = total_unrealized
        
        # 更新总资产
        self.account_balance['total_value'] = (
            self.account_balance['cash'] + 
            sum(pos['quantity'] * self.latest_prices.get(symbol, {'price': pos['avg_price']})['price'] 
                for symbol, pos in self.account_balance['positions'].items())
        )
    
    def place_order(self, symbol: str, side: OrderSide, order_type: OrderType,
                   quantity: float, price: Optional[float] = None,
                   client_order_id: str = None, strategy_name: str = None) -> Tuple[bool, str]:
        """
        下单
        
        Args:
            symbol: 交易对
            side: 买卖方向
            order_type: 订单类型
            quantity: 数量
            price: 价格（限价单需要）
            client_order_id: 客户端订单ID
            strategy_name: 策略名称
            
        Returns:
            (是否成功, 订单ID或错误信息)
        """
        try:
            # 生成订单ID
            order_id = client_order_id or str(uuid.uuid4())
            
            # 1. 风控检查
            risk_check, risk_message = self.risk_manager.check_order_risk(
                account_balance=self.account_balance,
                symbol=symbol,
                side=side,
                quantity=quantity,
                price=price or self.latest_prices.get(symbol, {'price': 0.0})['price']
            )
            
            if not risk_check:
                return False, f"风控检查失败: {risk_message}"
            
            # 2. 检查最小交易量
            min_qty = self.config['trading']['min_qty'].get(symbol, 0.0)
            if quantity < min_qty:
                return False, f"交易量低于最小值: {quantity} < {min_qty}"
            
            # 3. 检查可用资金
            if side == OrderSide.BUY:
                required_cash = quantity * (price or self.latest_prices.get(symbol, {'price': 0.0})['price'])
                if self.account_balance['cash'] < required_cash:
                    return False, f"可用资金不足: 需要{required_cash:.2f}, 可用{self.account_balance['cash']:.2f}"
            
            # 4. 创建交易记录
            trade_record = TradeRecord(
                trade_id=order_id,
                symbol=symbol,
                side=side,
                price=price or 0.0,  # 市价单暂时为0
                quantity=quantity,
                fee=0.0,  # 成交后计算
                order_type=order_type,
                status=OrderStatus.OPEN,
                timestamp=datetime.now(),
                client_order_id=client_order_id,
                strategy_name=strategy_name
            )
            
            # 5. 添加到挂单队列
            self.pending_orders[order_id] = trade_record
            
            # 6. 保存到数据库
            self.db_manager.save_trade_record(
                trade_id=trade_record.trade_id,
                symbol=trade_record.symbol,
                side=trade_record.side.value,
                price=trade_record.price,
                quantity=trade_record.quantity,
                fee=trade_record.fee,
                order_type=trade_record.order_type.value,
                status=trade_record.status.value,
                timestamp=trade_record.timestamp,
                realized_pnl=trade_record.realized_pnl
            )
            
            # 7. 放入交易队列
            self.trade_queue.put(('place', trade_record))
            
            print(f"订单已提交: {order_id} {symbol} {side.value} {quantity} @ {price if price else '市价'}")
            
            return True, order_id
            
        except Exception as e:
            print(f"下单失败: {e}")
            return False, str(e)
    
    def execute_order(self, order_id: str, execution_price: float) -> bool:
        """
        执行订单
        
        Args:
            order_id: 订单ID
            execution_price: 执行价格
            
        Returns:
            是否执行成功
        """
        if order_id not in self.pending_orders:
            print(f"订单不存在: {order_id}")
            return False
        
        trade_record = self.pending_orders[order_id]
        
        try:
            # 1. 计算手续费
            fee_rate = (self.config['trading']['fee']['maker'] 
                       if trade_record.order_type == OrderType.LIMIT 
                       else self.config['trading']['fee']['taker'])
            fee = trade_record.quantity * execution_price * fee_rate
            
            # 2. 更新交易记录
            trade_record.price = execution_price
            trade_record.fee = fee
            trade_record.status = OrderStatus.FILLED
            trade_record.filled_time = datetime.now()
            
            # 3. 更新账户
            self._update_account(trade_record)
            
            # 4. 计算已实现盈亏（如果有平仓）
            if trade_record.side == OrderSide.SELL:
                self._calculate_realized_pnl(trade_record)
            
            # 5. 移动订单到已成交
            self.filled_orders[order_id] = trade_record
            del self.pending_orders[order_id]
            
            # 6. 更新数据库
            self.db_manager.save_trade_record(
                trade_id=trade_record.trade_id,
                symbol=trade_record.symbol,
                side=trade_record.side.value,
                price=trade_record.price,
                quantity=trade_record.quantity,
                fee=trade_record.fee,
                order_type=trade_record.order_type.value,
                status=trade_record.status.value,
                timestamp=trade_record.timestamp,
                filled_time=trade_record.filled_time,
                realized_pnl=trade_record.realized_pnl
            )
            
            # 7. 添加到交易历史
            self.trade_history.append(trade_record)
            
            # 8. 更新性能指标
            self._update_performance_metrics()
            
            print(f"订单已执行: {order_id} {trade_record.symbol} {trade_record.side.value} "
                  f"{trade_record.quantity} @ {execution_price:.2f} "
                  f"手续费: {fee:.4f}")
            
            return True
            
        except Exception as e:
            print(f"执行订单失败: {e}")
            return False
    
    def _update_account(self, trade_record: TradeRecord):
        """更新账户信息"""
        symbol = trade_record.symbol
        quantity = trade_record.quantity
        price = trade_record.price
        fee = trade_record.fee
        
        if trade_record.side == OrderSide.BUY:
            # 买入
            total_cost = quantity * price + fee
            
            # 检查现金是否足够
            if self.account_balance['cash'] < total_cost:
                raise ValueError(f"现金不足: 需要{total_cost:.2f}, 可用{self.account_balance['cash']:.2f}")
            
            # 减少现金
            self.account_balance['cash'] -= total_cost
            
            # 更新持仓
            if symbol in self.account_balance['positions']:
                # 合并持仓
                position = self.account_balance['positions'][symbol]
                total_quantity = position['quantity'] + quantity
                total_value = (position['avg_price'] * position['quantity'] + 
                              price * quantity)
                new_avg_price = total_value / total_quantity
                
                position['quantity'] = total_quantity
                position['avg_price'] = new_avg_price
                position['direction'] = 'LONG'
            else:
                # 新建持仓
                self.account_balance['positions'][symbol] = {
                    'quantity': quantity,
                    'avg_price': price,
                    'direction': 'LONG'
                }
                
        else:  # SELL
            # 卖出
            if symbol not in self.account_balance['positions']:
                raise ValueError(f"没有持仓可卖出: {symbol}")
            
            position = self.account_balance['positions'][symbol]
            
            if position['direction'] != 'LONG':
                raise ValueError(f"持仓方向不匹配: {position['direction']}")
            
            if position['quantity'] < quantity:
                raise ValueError(f"持仓不足: 需要{quantity}, 持有{position['quantity']}")
            
            # 增加现金（减去手续费）
            sale_value = quantity * price
            net_cash = sale_value - fee
            self.account_balance['cash'] += net_cash
            
            # 更新持仓
            if position['quantity'] == quantity:
                # 全部卖出，移除持仓
                del self.account_balance['positions'][symbol]
            else:
                # 部分卖出
                position['quantity'] -= quantity
        
        # 更新总资产
        self._update_unrealized_pnl()
    
    def _calculate_realized_pnl(self, trade_record: TradeRecord):
        """计算已实现盈亏"""
        if trade_record.side != OrderSide.SELL:
            return
        
        symbol = trade_record.symbol
        sell_price = trade_record.price
        sell_quantity = trade_record.quantity
        
        # 获取平均买入价格
        if symbol in self.account_balance['positions']:
            avg_buy_price = self.account_balance['positions'][symbol]['avg_price']
            
            # 计算盈亏
            pnl = (sell_price - avg_buy_price) * sell_quantity - trade_record.fee
            
            trade_record.realized_pnl = pnl
            self.account_balance['realized_pnl'] += pnl
            
            print(f"已实现盈亏: {symbol} {pnl:.4f}")
    
    def cancel_order(self, order_id: str) -> bool:
        """
        取消订单
        
        Args:
            order_id: 订单ID
            
        Returns:
            是否取消成功
        """
        if order_id not in self.pending_orders:
            print(f"订单不存在: {order_id}")
            return False
        
        try:
            trade_record = self.pending_orders[order_id]
            trade_record.status = OrderStatus.CANCELLED
            
            # 更新数据库
            self.db_manager.save_trade_record(
                trade_id=trade_record.trade_id,
                symbol=trade_record.symbol,
                side=trade_record.side.value,
                price=trade_record.price,
                quantity=trade_record.quantity,
                fee=trade_record.fee,
                order_type=trade_record.order_type.value,
                status=trade_record.status.value,
                timestamp=trade_record.timestamp,
                realized_pnl=trade_record.realized_pnl
            )
            
            # 从挂单中移除
            del self.pending_orders[order_id]
            
            print(f"订单已取消: {order_id}")
            return True
            
        except Exception as e:
            print(f"取消订单失败: {e}")
            return False
    
    def get_order_status(self, order_id: str) -> Optional[Dict]:
        """
        获取订单状态
        
        Args:
            order_id: 订单ID
            
        Returns:
            订单状态信息
        """
        if order_id in self.pending_orders:
            trade_record = self.pending_orders[order_id]
            status = OrderStatus.OPEN
        elif order_id in self.filled_orders:
            trade_record = self.filled_orders[order_id]
            status = OrderStatus.FILLED
        else:
            return None
        
        return {
            'order_id': order_id,
            'symbol': trade_record.symbol,
            'side': trade_record.side.value,
            'price': trade_record.price,
            'quantity': trade_record.quantity,
            'order_type': trade_record.order_type.value,
            'status': status.value,
            'timestamp': trade_record.timestamp,
            'filled_time': trade_record.filled_time,
            'realized_pnl': trade_record.realized_pnl,
            'fee': trade_record.fee
        }
    
    def get_account_summary(self) -> Dict:
        """获取账户摘要"""
        return {
            'total_value': self.account_balance['total_value'],
            'cash': self.account_balance['cash'],
            'positions': self.account_balance['positions'],
            'unrealized_pnl': self.account_balance['unrealized_pnl'],
            'realized_pnl': self.account_balance['realized_pnl'],
            'performance': self.performance_metrics
        }
    
    def get_trade_history(self, limit: int = 100) -> List[Dict]:
        """获取交易历史"""
        recent_trades = self.trade_history[-limit:] if self.trade_history else []
        return [trade.to_dict() for trade in recent_trades]
    
    def _update_performance_metrics(self):
        """更新性能指标"""
        if not self.trade_history:
            return
        
        # 分析交易记录
        analysis = TradeAnalyzer.analyze_trades(self.trade_history)
        
        # 更新指标
        self.performance_metrics.update({
            'total_trades': analysis.get('total_trades', 0),
            'winning_trades': analysis.get('profitable_trades', 0),
            'losing_trades': analysis.get('losing_trades', 0),
            'total_commission': analysis.get('total_fee', 0.0),
            'win_rate': analysis.get('win_rate', 0.0)
        })
        
        # 计算回撤
        if len(self.trade_history) >= 2:
            pnl_series = pd.Series([trade.realized_pnl for trade in self.trade_history])
            drawdown_stats = TradeAnalyzer.calculate_drawdown(pnl_series)
            
            self.performance_metrics['max_drawdown'] = drawdown_stats.get('max_drawdown', 0.0)
            self.performance_metrics['current_drawdown'] = drawdown_stats.get('current_drawdown', 0.0)
    
    def start_processing(self):
        """启动订单处理线程"""
        self.running = True
        self.processing_thread = threading.Thread(target=self._process_orders)
        self.processing_thread.daemon = True
        self.processing_thread.start()
        print("订单处理线程已启动")
    
    def stop_processing(self):
        """停止订单处理线程"""
        self.running = False
        if self.processing_thread:
            self.processing_thread.join(timeout=5)
        print("订单处理线程已停止")
    
    def _process_orders(self):
        """处理订单队列"""
        while self.running:
            try:
                # 非阻塞获取队列项
                try:
                    action, data = self.trade_queue.get(timeout=1)
                except:
                    continue
                
                if action == 'place':
                    # 模拟订单执行（实际应该连接到交易所API）
                    self._simulate_order_execution(data)
                
                # 标记任务完成
                self.trade_queue.task_done()
                
            except Exception as e:
                print(f"处理订单时出错: {e}")
    
    def _simulate_order_execution(self, trade_record: TradeRecord):
        """模拟订单执行（测试用）"""
        if trade_record.order_type == OrderType.MARKET:
            # 市价单立即执行
            execution_price = self.latest_prices.get(trade_record.symbol, {'price': 100.0})['price']
            self.execute_order(trade_record.trade_id, execution_price)
        elif trade_record.order_type == OrderType.LIMIT:
            # 限价单等待价格匹配
            # 这里简化处理，实际应该监控价格变化
            current_price = self.latest_prices.get(trade_record.symbol, {'price': 0.0})['price']
            
            if trade_record.side == OrderSide.BUY and current_price <= trade_record.price:
                # 买入限价单，当前价格低于或等于限价
                self.execute_order(trade_record.trade_id, current_price)
            elif trade_record.side == OrderSide.SELL and current_price >= trade_record.price:
                # 卖出限价单，当前价格高于或等于限价
                self.execute_order(trade_record.trade_id, current_price)
    
    def get_pending_orders(self) -> Dict[str, Dict]:
        """获取所有挂单"""
        return {
            order_id: trade_record.to_dict()
            for order_id, trade_record in self.pending_orders.items()
        }
    
    def get_portfolio_value_history(self) -> pd.DataFrame:
        """获取投资组合价值历史"""
        # 从数据库获取历史快照
        return self.db_manager.get_portfolio_history()


if __name__ == "__main__":
    # 测试代码
    manager = TradeManager()
    
    # 启动处理线程
    manager.start_processing()
    
    try:
        # 模拟市场价格更新
        manager.update_market_price("BTCUSDT", 50000.0)
        manager.update_market_price("ETHUSDT", 3000.0)
        
        # 下测试单
        success, order_id = manager.place_order(
            symbol="BTCUSDT",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=0.001,
            strategy_name="测试策略"
        )
        
        if success:
            print(f"下单成功: {order_id}")
        else:
            print(f"下单失败: {order_id}")
        
        # 等待一段时间
        time.sleep(2)
        
        # 获取账户摘要
        summary = manager.get_account_summary()
        print(f"账户摘要: {summary}")
        
    finally:
        manager.stop_processing()