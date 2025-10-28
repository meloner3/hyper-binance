"""
币安交易API模块
用于执行开空单操作
"""
from binance.client import Client
from binance.enums import *
from binance.exceptions import BinanceAPIException
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)


class BinanceTrader:
    """币安交易类"""
    
    def __init__(self, api_key: str, api_secret: str, testnet: bool = False):
        """
        初始化币安交易客户端
        
        Args:
            api_key: API密钥
            api_secret: API密钥
            testnet: 是否使用测试网
        """
        try:
            if testnet:
                self.client = Client(api_key, api_secret, testnet=True)
                logger.info("使用币安测试网")
            else:
                self.client = Client(api_key, api_secret)
                logger.info("使用币安正式网")
            
            # 测试连接
            self.client.ping()
            logger.info("币安API连接成功")
            
        except Exception as e:
            logger.error(f"初始化币安客户端失败: {e}")
            raise
    
    def set_leverage(self, symbol: str, leverage: int) -> bool:
        """
        设置杠杆倍数
        
        Args:
            symbol: 交易对符号
            leverage: 杠杆倍数
            
        Returns:
            是否成功
        """
        try:
            response = self.client.futures_change_leverage(
                symbol=symbol,
                leverage=leverage
            )
            logger.info(f"设置 {symbol} 杠杆为 {leverage}x: {response}")
            return True
        except BinanceAPIException as e:
            logger.error(f"设置杠杆失败: {e}")
            return False
        except Exception as e:
            logger.error(f"设置杠杆时发生错误: {e}")
            return False
    
    def set_margin_type(self, symbol: str, margin_type: str = 'CROSSED') -> bool:
        """
        设置保证金模式
        
        Args:
            symbol: 交易对符号
            margin_type: 保证金类型 ('ISOLATED' 或 'CROSSED')
            
        Returns:
            是否成功
        """
        try:
            response = self.client.futures_change_margin_type(
                symbol=symbol,
                marginType=margin_type
            )
            logger.info(f"设置 {symbol} 保证金模式为 {margin_type}: {response}")
            return True
        except BinanceAPIException as e:
            # 如果已经是该模式，会返回错误，但这不是问题
            if 'No need to change margin type' in str(e):
                logger.info(f"{symbol} 已经是 {margin_type} 模式")
                return True
            logger.error(f"设置保证金模式失败: {e}")
            return False
        except Exception as e:
            logger.error(f"设置保证金模式时发生错误: {e}")
            return False
    
    def get_symbol_info(self, symbol: str) -> Optional[Dict]:
        """
        获取交易对信息
        
        Args:
            symbol: 交易对符号
            
        Returns:
            交易对信息字典或None
        """
        try:
            exchange_info = self.client.futures_exchange_info()
            for s in exchange_info['symbols']:
                if s['symbol'] == symbol:
                    return s
            return None
        except Exception as e:
            logger.error(f"获取交易对信息失败: {e}")
            return None
    
    def calculate_quantity(self, symbol: str, usdc_amount: float, leverage: int = 1, current_price: Optional[float] = None) -> float:
        """
        计算交易数量
        
        Args:
            symbol: 交易对符号
            usdc_amount: USDC金额（保证金金额）
            leverage: 杠杆倍数
            current_price: 当前价格（如果为None则获取市场价格）
            
        Returns:
            交易数量
        """
        try:
            # 获取当前价格
            if current_price is None:
                ticker = self.client.futures_symbol_ticker(symbol=symbol)
                current_price = float(ticker['price'])
            
            # 获取交易对信息以确定精度
            symbol_info = self.get_symbol_info(symbol)
            if not symbol_info:
                logger.error(f"无法获取 {symbol} 的交易对信息")
                return 0
            
            # 计算数量：保证金 × 杠杆 / 价格
            position_value = usdc_amount * leverage
            quantity = position_value / current_price
            
            # 根据交易对的精度要求调整数量
            for filter_item in symbol_info['filters']:
                if filter_item['filterType'] == 'LOT_SIZE':
                    step_size = float(filter_item['stepSize'])
                    precision = len(str(step_size).rstrip('0').split('.')[-1])
                    quantity = round(quantity, precision)
                    break
            
            logger.info(f"{symbol} 计算数量: {quantity} (价格: {current_price}, 保证金: {usdc_amount}, 杠杆: {leverage}x, 持仓价值: {position_value})")
            return quantity
            
        except Exception as e:
            logger.error(f"计算交易数量时发生错误: {e}")
            return 0
    
    def open_short_position(self, symbol: str, quantity: float) -> Optional[Dict]:
        """
        开空单
        
        Args:
            symbol: 交易对符号
            quantity: 交易数量
            
        Returns:
            订单信息或None
        """
        try:
            # 使用市价单开空
            order = self.client.futures_create_order(
                symbol=symbol,
                side=SIDE_SELL,
                type=ORDER_TYPE_MARKET,
                quantity=quantity,
                positionSide='SHORT'  # 指定持仓方向为空头
            )
            
            logger.info(f"成功开空 {symbol}: {order}")
            return order
            
        except BinanceAPIException as e:
            logger.error(f"开空单失败 (API错误): {e}")
            return None
        except Exception as e:
            logger.error(f"开空单时发生错误: {e}")
            return None
    
    def execute_short_trade(self, coin: str, symbol: str, leverage: int, usdc_amount: float) -> bool:
        """
        执行完整的开空交易流程
        
        Args:
            coin: 币种 (ETH/BTC)
            symbol: 交易对符号
            leverage: 杠杆倍数
            usdc_amount: USDC保证金金额
            
        Returns:
            是否成功
        """
        try:
            position_value = usdc_amount * leverage
            logger.info(f"开始执行 {coin} 开空交易: {symbol}, 杠杆: {leverage}x, 保证金: {usdc_amount} USDC, 持仓价值: {position_value} USDC")
            
            # 1. 设置保证金模式（全仓）
            self.set_margin_type(symbol, 'CROSSED')
            
            # 2. 设置杠杆
            if not self.set_leverage(symbol, leverage):
                logger.error(f"设置杠杆失败，取消交易")
                return False
            
            # 3. 获取当前价格
            ticker = self.client.futures_symbol_ticker(symbol=symbol)
            current_price = float(ticker['price'])
            logger.info(f"当前 {coin} 价格: {current_price} USDC")
            
            # 4. 计算交易数量
            quantity = self.calculate_quantity(symbol, usdc_amount, leverage, current_price)
            if quantity <= 0:
                logger.error(f"计算数量失败，取消交易")
                return False
            
            logger.info(f"计算交易数量: {quantity} {coin}, 预估持仓价值: {quantity * current_price:.2f} USDC")
            
            # 5. 执行开空
            order = self.open_short_position(symbol, quantity)
            if order:
                logger.info(f"✅ {coin} 开空成功! 订单ID: {order.get('orderId')}")
                
                # 显示订单详情
                if 'avgPrice' in order and order['avgPrice']:
                    avg_price = float(order['avgPrice'])
                    actual_value = quantity * avg_price
                    logger.info(f"成交均价: {avg_price}, 实际持仓价值: {actual_value:.2f} USDC")
                
                return True
            else:
                logger.error(f"❌ {coin} 开空失败")
                return False
                
        except Exception as e:
            logger.error(f"执行交易时发生错误: {e}", exc_info=True)
            return False
    
    def get_account_balance(self) -> Optional[Dict]:
        """
        获取账户余额
        
        Returns:
            账户余额信息
        """
        try:
            balance = self.client.futures_account_balance()
            return balance
        except Exception as e:
            logger.error(f"获取账户余额失败: {e}")
            return None
    
    def get_position_info(self, symbol: Optional[str] = None) -> Optional[list]:
        """
        获取持仓信息
        
        Args:
            symbol: 交易对符号（可选）
            
        Returns:
            持仓信息列表
        """
        try:
            positions = self.client.futures_position_information(symbol=symbol)
            return positions
        except Exception as e:
            logger.error(f"获取持仓信息失败: {e}")
            return None
    
    def get_account_info_summary(self) -> Optional[Dict]:
        """
        获取账户信息摘要（用于启动通知）
        
        Returns:
            包含余额和持仓信息的字典
        """
        try:
            # 获取账户余额
            balance_list = self.get_account_balance()
            balances = {}
            total_balance = 0
            
            if balance_list:
                for item in balance_list:
                    asset = item['asset']
                    balance = float(item['balance'])
                    if balance > 0:
                        balances[asset] = balance
                        if asset == 'USDT':
                            total_balance = balance
            
            # 获取所有持仓
            all_positions = self.get_position_info()
            active_positions = []
            
            if all_positions:
                for pos in all_positions:
                    position_amt = float(pos.get('positionAmt', 0))
                    if position_amt != 0:
                        symbol = pos.get('symbol', '')
                        entry_price = float(pos.get('entryPrice', 0))
                        unrealized_pnl = float(pos.get('unRealizedProfit', 0))
                        leverage = pos.get('leverage', '0')
                        position_value = abs(position_amt) * entry_price
                        
                        active_positions.append({
                            'symbol': symbol,
                            'side': '多头' if position_amt > 0 else '空头',
                            'quantity': abs(position_amt),
                            'entry_price': entry_price,
                            'position_value': position_value,
                            'unrealized_pnl': unrealized_pnl,
                            'leverage': leverage
                        })
            
            return {
                'balances': balances,
                'total_balance': total_balance,
                'positions': active_positions
            }
            
        except Exception as e:
            logger.error(f"获取账户信息摘要失败: {e}")
            return None

