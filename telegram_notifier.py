"""
Telegram通知模块
用于发送交易通知和系统状态消息
"""
import logging
import asyncio
from typing import Optional
from datetime import datetime
from telegram import Bot
from telegram.error import TelegramError

logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Telegram通知类"""
    
    def __init__(self, bot_token: str, chat_id: str, enabled: bool = True):
        """
        初始化Telegram通知器
        
        Args:
            bot_token: Telegram Bot Token
            chat_id: 接收消息的Chat ID
            enabled: 是否启用通知
        """
        self.enabled = enabled
        self.chat_id = chat_id
        self.bot = None
        self.send_count = 0
        self.error_count = 0
        
        if not enabled:
            logger.info("Telegram通知已禁用")
            return
        
        if not bot_token or bot_token == 'your_telegram_bot_token_here':
            logger.warning("⚠️  未配置Telegram Bot Token，通知功能将被禁用")
            self.enabled = False
            return
        
        if not chat_id or chat_id == 'your_telegram_chat_id_here':
            logger.warning("⚠️  未配置Telegram Chat ID，通知功能将被禁用")
            self.enabled = False
            return
        
        try:
            self.bot = Bot(token=bot_token)
            logger.info("✅ Telegram通知器初始化成功")
        except Exception as e:
            logger.error(f"❌ Telegram通知器初始化失败: {e}")
            self.enabled = False
    
    async def _send_message_async(self, message: str, parse_mode: str = 'HTML') -> bool:
        """
        异步发送消息
        
        Args:
            message: 消息内容
            parse_mode: 解析模式 (HTML/Markdown)
            
        Returns:
            是否发送成功
        """
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode=parse_mode
            )
            self.send_count += 1
            logger.debug(f"Telegram消息发送成功 (总计: {self.send_count})")
            return True
        except TelegramError as e:
            self.error_count += 1
            logger.error(f"Telegram消息发送失败: {e}")
            return False
        except Exception as e:
            self.error_count += 1
            logger.error(f"发送Telegram消息时发生错误: {e}")
            return False
    
    def send_message(self, message: str, parse_mode: str = 'HTML') -> bool:
        """
        发送消息（同步接口）
        
        Args:
            message: 消息内容
            parse_mode: 解析模式 (HTML/Markdown)
            
        Returns:
            是否发送成功
        """
        if not self.enabled:
            return False
        
        try:
            # 尝试获取当前事件循环
            try:
                loop = asyncio.get_event_loop()
                if loop.is_closed():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
            except RuntimeError:
                # 如果没有事件循环，创建一个新的
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # 运行异步函数
            result = loop.run_until_complete(self._send_message_async(message, parse_mode))
            return result
        except Exception as e:
            logger.error(f"发送Telegram消息时发生错误: {e}")
            return False
    
    def send_startup_message(self, monitor_address: str, config_info: dict):
        """
        发送系统启动消息
        
        Args:
            monitor_address: 监控地址
            config_info: 配置信息字典
        """
        if not self.enabled:
            return
        
        try:
            message = f"""
🤖 <b>系统启动通知</b>

⏰ 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📋 <b>配置信息:</b>
• 监控地址: <code>{monitor_address[:10]}...{monitor_address[-8:]}</code>
• 扫描间隔: {config_info.get('scan_interval', 'N/A')}秒
• 杠杆倍数: {config_info.get('leverage', 'N/A')}x
• 保证金: {config_info.get('position_size', 'N/A')} USDC
• 持仓价值: {config_info.get('position_value', 'N/A')} USDC
• 交易对: {config_info.get('trading_pairs', 'N/A')}

✅ 系统已启动，开始监控...
"""
            self.send_message(message)
            logger.info("✅ 已发送系统启动通知")
        except Exception as e:
            logger.error(f"发送启动消息失败: {e}")
    
    def send_binance_account_info(self, account_info: dict):
        """
        发送币安账户信息
        
        Args:
            account_info: 账户信息字典
        """
        if not self.enabled:
            return
        
        try:
            balances = account_info.get('balances', {})
            positions = account_info.get('positions', [])
            
            # 构建余额信息
            balance_text = ""
            if balances:
                for asset, balance in balances.items():
                    balance_text += f"• {asset}: {balance:,.2f}\n"
            else:
                balance_text = "• 暂无余额信息\n"
            
            # 构建持仓信息
            position_text = ""
            if positions:
                for pos in positions:
                    side_emoji = "🟢" if pos['side'] == '多头' else "🔴"
                    pnl_emoji = "💰" if pos['unrealized_pnl'] >= 0 else "📉"
                    position_text += f"\n<b>{pos['symbol']}</b> {side_emoji}\n"
                    position_text += f"  方向: {pos['side']}\n"
                    position_text += f"  数量: {pos['quantity']}\n"
                    position_text += f"  入场价: ${pos['entry_price']:,.2f}\n"
                    position_text += f"  持仓价值: ${pos['position_value']:,.2f}\n"
                    position_text += f"  杠杆: {pos['leverage']}x\n"
                    position_text += f"  未实现盈亏: {pnl_emoji} ${pos['unrealized_pnl']:,.2f}\n"
            else:
                position_text = "\n• 当前无持仓\n"
            
            message = f"""
💼 <b>币安合约账户信息</b>

💰 <b>账户余额:</b>
{balance_text}
📊 <b>当前持仓:</b>
{position_text}
"""
            self.send_message(message)
            logger.info("✅ 已发送币安账户信息")
        except Exception as e:
            logger.error(f"发送币安账户信息失败: {e}")
    
    def send_hyperliquid_positions(self, positions_info: dict):
        """
        发送Hyperliquid持仓信息
        
        Args:
            positions_info: 持仓信息字典
        """
        if not self.enabled:
            return
        
        try:
            positions = positions_info.get('positions', [])
            account_value = positions_info.get('account_value', 0)
            total_margin_used = positions_info.get('total_margin_used', 0)
            available_balance = positions_info.get('available_balance', 0)
            
            # 构建持仓信息
            position_text = ""
            if positions:
                for pos in positions:
                    side_emoji = "🟢" if pos['side'] == '多头' else "🔴"
                    pnl_emoji = "💰" if pos['unrealized_pnl'] >= 0 else "📉"
                    position_text += f"\n<b>{pos['coin']}</b> {side_emoji}\n"
                    position_text += f"  方向: {pos['side']}\n"
                    position_text += f"  持仓量: {pos['size']}\n"
                    position_text += f"  入场价: ${pos['entry_price']:,.2f}\n"
                    position_text += f"  持仓价值: ${pos['position_value']:,.2f}\n"
                    position_text += f"  杠杆: {pos['leverage']}x\n"
                    position_text += f"  已用保证金: ${pos['margin_used']:,.2f}\n"
                    position_text += f"  未实现盈亏: {pnl_emoji} ${pos['unrealized_pnl']:,.2f}\n"
                    if pos['liquidation_price']:
                        position_text += f"  强平价格: ${pos['liquidation_price']:,.2f}\n"
            else:
                position_text = "\n• 当前无持仓\n"
            
            message = f"""
📊 <b>监控地址持仓信息</b>

💼 <b>账户总览:</b>
• 账户价值: ${account_value:,.2f}
• 已用保证金: ${total_margin_used:,.2f}
• 可用余额: ${available_balance:,.2f}

📈 <b>当前持仓:</b>
{position_text}
"""
            self.send_message(message)
            logger.info("✅ 已发送Hyperliquid持仓信息")
        except Exception as e:
            logger.error(f"发送Hyperliquid持仓信息失败: {e}")
    
    def send_position_close_alert(self, position_info: dict):
        """
        发送平仓检测警报
        
        Args:
            position_info: 平仓信息字典
        """
        if not self.enabled:
            return
        
        try:
            coin = position_info.get('coin', 'UNKNOWN')
            size = position_info.get('size', 0)
            price = position_info.get('price', 0)
            closed_pnl = position_info.get('closed_pnl', 0)
            datetime_str = position_info.get('datetime', 'N/A')
            
            # 根据盈亏显示emoji
            pnl_emoji = '💰' if closed_pnl > 0 else '📉'
            
            message = f"""
🚨 <b>检测到平多仓操作！</b>

📊 <b>交易信息:</b>
• 币种: <b>{coin}</b>
• 数量: {size}
• 价格: ${price:,.2f}
• 已实现盈亏: {pnl_emoji} ${closed_pnl:,.2f}
• 时间: {datetime_str}

⚡️ 准备在币安开空单...
"""
            self.send_message(message)
            logger.info(f"✅ 已发送平仓检测通知: {coin}")
        except Exception as e:
            logger.error(f"发送平仓警报失败: {e}")
    
    def send_trade_success(self, trade_info: dict):
        """
        发送交易成功通知
        
        Args:
            trade_info: 交易信息字典
        """
        if not self.enabled:
            return
        
        try:
            coin = trade_info.get('coin', 'UNKNOWN')
            symbol = trade_info.get('symbol', 'UNKNOWN')
            leverage = trade_info.get('leverage', 0)
            margin = trade_info.get('margin', 0)
            position_value = trade_info.get('position_value', 0)
            quantity = trade_info.get('quantity', 0)
            entry_price = trade_info.get('entry_price', 0)
            order_id = trade_info.get('order_id', 'N/A')
            
            message = f"""
✅ <b>开空单成功！</b>

💼 <b>交易详情:</b>
• 币种: <b>{coin}</b> ({symbol})
• 订单ID: <code>{order_id}</code>
• 杠杆: {leverage}x
• 保证金: ${margin:,.2f}
• 持仓价值: ${position_value:,.2f}
• 数量: {quantity}
• 入场价格: ${entry_price:,.2f}

📈 持仓已建立，请注意风险管理！
"""
            self.send_message(message)
            logger.info(f"✅ 已发送交易成功通知: {coin}")
        except Exception as e:
            logger.error(f"发送交易成功通知失败: {e}")
    
    def send_trade_failure(self, coin: str, error_msg: str):
        """
        发送交易失败通知
        
        Args:
            coin: 币种
            error_msg: 错误信息
        """
        if not self.enabled:
            return
        
        try:
            message = f"""
❌ <b>开空单失败！</b>

• 币种: <b>{coin}</b>
• 错误信息: {error_msg}
• 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

⚠️ 请检查系统日志了解详情
"""
            self.send_message(message)
            logger.info(f"✅ 已发送交易失败通知: {coin}")
        except Exception as e:
            logger.error(f"发送交易失败通知失败: {e}")
    
    def send_api_test_result(self, success: bool, latest_fill: dict = None):
        """
        发送API测试结果
        
        Args:
            success: 是否成功
            latest_fill: 最近一笔订单信息
        """
        if not self.enabled:
            return
        
        try:
            if success and latest_fill:
                coin = latest_fill.get('coin', 'UNKNOWN')
                datetime_str = latest_fill.get('datetime', 'N/A')
                
                message = f"""
✅ <b>API接口测试成功</b>

📝 最近一笔订单:
• 币种: {coin}
• 时间: {datetime_str}

🔍 系统正常，开始监控...
"""
            else:
                message = f"""
⚠️ <b>API接口测试失败</b>

可能原因:
• 网络连接问题
• API服务器暂时不可用
• 该地址暂无交易记录

⚡️ 程序将继续运行并重试
"""
            
            self.send_message(message)
            logger.info("✅ 已发送API测试结果通知")
        except Exception as e:
            logger.error(f"发送API测试结果失败: {e}")
    
    def send_error_alert(self, error_type: str, error_msg: str):
        """
        发送错误警报
        
        Args:
            error_type: 错误类型
            error_msg: 错误信息
        """
        if not self.enabled:
            return
        
        try:
            message = f"""
⚠️ <b>系统错误警报</b>

• 错误类型: {error_type}
• 错误信息: {error_msg}
• 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

请检查系统状态
"""
            self.send_message(message)
            logger.info(f"✅ 已发送错误警报: {error_type}")
        except Exception as e:
            logger.error(f"发送错误警报失败: {e}")
    
    def test_connection(self) -> bool:
        """
        测试Telegram连接
        
        Returns:
            是否连接成功
        """
        if not self.enabled:
            logger.warning("Telegram通知未启用")
            return False
        
        try:
            message = f"""
🧪 <b>Telegram通知测试</b>

✅ 连接成功！
⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

如果您收到此消息，说明Telegram通知配置正确。
"""
            result = self.send_message(message)
            if result:
                logger.info("✅ Telegram连接测试成功")
            else:
                logger.error("❌ Telegram连接测试失败")
            return result
        except Exception as e:
            logger.error(f"Telegram连接测试失败: {e}")
            return False

