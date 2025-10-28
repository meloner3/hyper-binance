"""
主程序 - 监控Hyperliquid地址并自动在币安开空单
"""
import logging
from typing import Dict
import signal
import sys

from config import (
    BINANCE_API_KEY,
    BINANCE_API_SECRET,
    MONITOR_ADDRESS,
    SCAN_INTERVAL,
    POSITION_PRINT_INTERVAL,
    USER_FILLS_LIMIT,
    LEVERAGE,
    POSITION_SIZE_USDC,
    HYPERLIQUID_API_URL,
    TRADING_PAIRS,
    LOG_FILE,
    LOG_LEVEL,
    USE_TESTNET,
    TELEGRAM_ENABLED,
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID
)
from logger_config import setup_logger
from hyperliquid_monitor import HyperliquidMonitor
from binance_trader import BinanceTrader
from telegram_notifier import TelegramNotifier

logger = logging.getLogger(__name__)


class TradingBot:
    """交易机器人主类"""
    
    def __init__(self):
        """初始化交易机器人"""
        self.running = True
        
        # 初始化Telegram通知器
        logger.info("初始化Telegram通知器...")
        self.notifier = TelegramNotifier(
            bot_token=TELEGRAM_BOT_TOKEN,
            chat_id=TELEGRAM_CHAT_ID,
            enabled=TELEGRAM_ENABLED
        )
        
        # 初始化Hyperliquid监控器
        logger.info("初始化Hyperliquid监控器...")
        self.monitor = HyperliquidMonitor(
            api_url=HYPERLIQUID_API_URL,
            monitor_address=MONITOR_ADDRESS,
            user_fills_limit=USER_FILLS_LIMIT
        )
        
        # 初始化币安交易客户端
        logger.info("初始化币安交易客户端...")
        if not BINANCE_API_KEY or BINANCE_API_KEY == 'your_binance_api_key_here':
            logger.error("❌ 未配置币安API密钥，请在config.py文件中配置")
            raise ValueError("未配置币安API密钥")
        
        self.trader = BinanceTrader(
            api_key=BINANCE_API_KEY,
            api_secret=BINANCE_API_SECRET,
            testnet=USE_TESTNET
        )
        
        # 设置信号处理
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        logger.info("✅ 交易机器人初始化完成")
    
    def signal_handler(self, signum, frame):
        """信号处理函数"""
        logger.info(f"收到信号 {signum}，准备退出...")
        self.running = False
        sys.exit(0)
    
    def on_close_position_detected(self, position: Dict):
        """
        当检测到平仓操作时的回调函数
        
        Args:
            position: 平仓信息字典
        """
        try:
            coin = position['coin']
            size = position['size']
            price = position['price']
            closed_pnl = position['closed_pnl']
            datetime_str = position['datetime']
            
            logger.warning("=" * 80)
            logger.warning(f"🚨 检测到平多仓操作!")
            logger.warning(f"币种: {coin}")
            logger.warning(f"数量: {size}")
            logger.warning(f"价格: {price}")
            logger.warning(f"已实现盈亏: {closed_pnl}")
            logger.warning(f"时间: {datetime_str}")
            logger.warning("=" * 80)
            
            # 发送Telegram通知
            self.notifier.send_position_close_alert(position)
            
            # 检查是否为ETH或BTC
            if coin not in TRADING_PAIRS:
                logger.warning(f"⚠️  币种 {coin} 不在交易列表中，跳过")
                return
            
            # 获取对应的交易对
            symbol = TRADING_PAIRS[coin]
            
            position_value = POSITION_SIZE_USDC * LEVERAGE
            logger.info(f"准备在币安开空 {coin} ({symbol})...")
            logger.info(f"杠杆: {LEVERAGE}x, 保证金: {POSITION_SIZE_USDC} USDC, 持仓价值: {position_value} USDC")
            
            # 执行开空交易
            success = self.trader.execute_short_trade(
                coin=coin,
                symbol=symbol,
                leverage=LEVERAGE,
                usdc_amount=POSITION_SIZE_USDC
            )
            
            if success:
                logger.warning(f"✅ 成功在币安开空 {coin}!")
                
                # 获取并显示持仓信息
                positions = self.trader.get_position_info(symbol)
                trade_info = {
                    'coin': coin,
                    'symbol': symbol,
                    'leverage': LEVERAGE,
                    'margin': POSITION_SIZE_USDC,
                    'position_value': position_value,
                    'quantity': 0,
                    'entry_price': 0,
                    'order_id': 'N/A'
                }
                
                if positions:
                    for pos in positions:
                        position_amt = float(pos.get('positionAmt', 0))
                        if position_amt != 0:
                            entry_price = float(pos.get('entryPrice', 0))
                            unrealized_pnl = float(pos.get('unRealizedProfit', 0))
                            logger.info(f"当前 {coin} 持仓:")
                            logger.info(f"  持仓量: {pos.get('positionAmt')}")
                            logger.info(f"  入场价格: {entry_price}")
                            logger.info(f"  持仓价值: {abs(position_amt) * entry_price:.2f} USDC")
                            logger.info(f"  未实现盈亏: {unrealized_pnl} USDC")
                            logger.info(f"  杠杆: {pos.get('leverage')}x")
                            
                            # 更新交易信息
                            trade_info['quantity'] = abs(position_amt)
                            trade_info['entry_price'] = entry_price
                
                # 发送交易成功通知
                self.notifier.send_trade_success(trade_info)
            else:
                logger.error(f"❌ 在币安开空 {coin} 失败!")
                # 发送交易失败通知
                self.notifier.send_trade_failure(coin, "开空单失败，请查看日志")
            
            logger.warning("=" * 80)
            
        except Exception as e:
            logger.error(f"处理平仓事件时发生错误: {e}", exc_info=True)
    
    def display_startup_info(self):
        """显示启动信息"""
        logger.info("")
        logger.info("=" * 80)
        logger.info("🤖 Hyperliquid监控交易机器人")
        logger.info("=" * 80)
        logger.info(f"监控地址: {MONITOR_ADDRESS}")
        logger.info(f"扫描间隔: {SCAN_INTERVAL}秒")
        logger.info(f"杠杆倍数: {LEVERAGE}x")
        logger.info(f"持仓量: {POSITION_SIZE_USDC} USDC")
        logger.info(f"交易对: {', '.join([f'{k}→{v}' for k, v in TRADING_PAIRS.items()])}")
        logger.info(f"测试模式: {'是' if USE_TESTNET else '否'}")
        logger.info(f"Telegram通知: {'启用' if TELEGRAM_ENABLED and self.notifier.enabled else '禁用'}")
        logger.info("=" * 80)
        logger.info("")
        
        # 显示账户余额
        try:
            balance = self.trader.get_account_balance()
            if balance:
                logger.info("📊 币安账户余额:")
                for item in balance:
                    if float(item['balance']) > 0:
                        logger.info(f"  {item['asset']}: {item['balance']}")
                logger.info("")
        except Exception as e:
            logger.warning(f"无法获取账户余额: {e}")
        
        # 发送启动通知
        position_value = POSITION_SIZE_USDC * LEVERAGE
        config_info = {
            'scan_interval': SCAN_INTERVAL,
            'leverage': LEVERAGE,
            'position_size': POSITION_SIZE_USDC,
            'position_value': position_value,
            'trading_pairs': ', '.join([f'{k}→{v}' for k, v in TRADING_PAIRS.items()])
        }
        self.notifier.send_startup_message(MONITOR_ADDRESS, config_info)
        
        # 推送币安账户信息到Telegram
        try:
            logger.info("正在获取币安账户信息...")
            binance_account_info = self.trader.get_account_info_summary()
            if binance_account_info:
                self.notifier.send_binance_account_info(binance_account_info)
                logger.info("✅ 已推送币安账户信息到Telegram")
            else:
                logger.warning("⚠️  无法获取币安账户信息")
        except Exception as e:
            logger.error(f"获取币安账户信息失败: {e}")
        
        # 推送监控地址持仓信息到Telegram
        try:
            logger.info("正在获取监控地址持仓信息...")
            hyperliquid_positions = self.monitor.get_positions_summary()
            if hyperliquid_positions:
                self.notifier.send_hyperliquid_positions(hyperliquid_positions)
                logger.info("✅ 已推送监控地址持仓信息到Telegram")
            else:
                logger.warning("⚠️  无法获取监控地址持仓信息")
        except Exception as e:
            logger.error(f"获取监控地址持仓信息失败: {e}")
    
    def run(self):
        """运行机器人"""
        try:
            self.display_startup_info()
            
            logger.info("🚀 开始监控...")
            logger.info("按 Ctrl+C 停止监控")
            logger.info("")
            
            # 开始监控
            self.monitor.start_monitoring(
                scan_interval=SCAN_INTERVAL,
                callback=self.on_close_position_detected,
                position_print_interval=POSITION_PRINT_INTERVAL
            )
            
        except KeyboardInterrupt:
            logger.info("用户中断，停止监控")
        except Exception as e:
            logger.error(f"运行时发生错误: {e}", exc_info=True)
        finally:
            logger.info("机器人已停止")


def main():
    """主函数"""
    # 设置日志
    setup_logger(log_file=LOG_FILE, log_level=LOG_LEVEL)
    
    try:
        # 创建并运行机器人
        bot = TradingBot()
        bot.run()
        
    except Exception as e:
        logger.error(f"程序启动失败: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
