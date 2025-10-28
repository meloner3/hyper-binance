"""
测试启动通知功能
测试币安账户信息和Hyperliquid持仓信息推送
"""
import logging
from config import (
    BINANCE_API_KEY,
    BINANCE_API_SECRET,
    MONITOR_ADDRESS,
    USE_TESTNET,
    TELEGRAM_ENABLED,
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID,
    HYPERLIQUID_API_URL
)
from logger_config import setup_logger
from binance_trader import BinanceTrader
from hyperliquid_monitor import HyperliquidMonitor
from telegram_notifier import TelegramNotifier

# 设置日志
setup_logger(log_file='test_startup.log', log_level='INFO')
logger = logging.getLogger(__name__)


def test_binance_account_info():
    """测试获取币安账户信息"""
    logger.info("=" * 80)
    logger.info("测试币安账户信息获取")
    logger.info("=" * 80)
    
    try:
        # 初始化币安交易客户端
        trader = BinanceTrader(
            api_key=BINANCE_API_KEY,
            api_secret=BINANCE_API_SECRET,
            testnet=USE_TESTNET
        )
        
        # 获取账户信息摘要
        account_info = trader.get_account_info_summary()
        
        if account_info:
            logger.info("✅ 成功获取账户信息")
            logger.info(f"余额: {account_info.get('balances', {})}")
            logger.info(f"总余额: {account_info.get('total_balance', 0)}")
            logger.info(f"持仓数量: {len(account_info.get('positions', []))}")
            
            # 显示持仓详情
            positions = account_info.get('positions', [])
            if positions:
                logger.info("\n当前持仓:")
                for pos in positions:
                    logger.info(f"  {pos['symbol']}: {pos['side']}, 数量: {pos['quantity']}, "
                              f"入场价: {pos['entry_price']}, 未实现盈亏: {pos['unrealized_pnl']}")
            else:
                logger.info("当前无持仓")
            
            return account_info
        else:
            logger.error("❌ 获取账户信息失败")
            return None
            
    except Exception as e:
        logger.error(f"测试失败: {e}", exc_info=True)
        return None


def test_hyperliquid_positions():
    """测试获取Hyperliquid持仓信息"""
    logger.info("")
    logger.info("=" * 80)
    logger.info("测试Hyperliquid持仓信息获取")
    logger.info("=" * 80)
    
    try:
        # 初始化监控器
        monitor = HyperliquidMonitor(
            api_url=HYPERLIQUID_API_URL,
            monitor_address=MONITOR_ADDRESS,
            user_fills_limit=20
        )
        
        # 获取持仓信息摘要
        positions_info = monitor.get_positions_summary()
        
        if positions_info:
            logger.info("✅ 成功获取持仓信息")
            logger.info(f"账户价值: ${positions_info.get('account_value', 0):,.2f}")
            logger.info(f"已用保证金: ${positions_info.get('total_margin_used', 0):,.2f}")
            logger.info(f"可用余额: ${positions_info.get('available_balance', 0):,.2f}")
            logger.info(f"持仓数量: {len(positions_info.get('positions', []))}")
            
            # 显示持仓详情
            positions = positions_info.get('positions', [])
            if positions:
                logger.info("\n当前持仓:")
                for pos in positions:
                    logger.info(f"  {pos['coin']}: {pos['side']}, 持仓量: {pos['size']}, "
                              f"入场价: ${pos['entry_price']:,.2f}, 未实现盈亏: ${pos['unrealized_pnl']:,.2f}")
            else:
                logger.info("当前无持仓")
            
            return positions_info
        else:
            logger.error("❌ 获取持仓信息失败")
            return None
            
    except Exception as e:
        logger.error(f"测试失败: {e}", exc_info=True)
        return None


def test_telegram_notifications(binance_info, hyperliquid_info):
    """测试Telegram通知发送"""
    logger.info("")
    logger.info("=" * 80)
    logger.info("测试Telegram通知发送")
    logger.info("=" * 80)
    
    try:
        # 初始化Telegram通知器
        notifier = TelegramNotifier(
            bot_token=TELEGRAM_BOT_TOKEN,
            chat_id=TELEGRAM_CHAT_ID,
            enabled=TELEGRAM_ENABLED
        )
        
        if not notifier.enabled:
            logger.warning("⚠️  Telegram通知未启用，跳过测试")
            return
        
        # 发送币安账户信息
        if binance_info:
            logger.info("发送币安账户信息...")
            notifier.send_binance_account_info(binance_info)
            logger.info("✅ 已发送币安账户信息")
        
        # 发送Hyperliquid持仓信息
        if hyperliquid_info:
            logger.info("发送Hyperliquid持仓信息...")
            notifier.send_hyperliquid_positions(hyperliquid_info)
            logger.info("✅ 已发送Hyperliquid持仓信息")
        
        logger.info("✅ Telegram通知测试完成")
        
    except Exception as e:
        logger.error(f"测试失败: {e}", exc_info=True)


def main():
    """主测试函数"""
    logger.info("开始测试启动通知功能")
    logger.info("")
    
    # 测试币安账户信息
    binance_info = test_binance_account_info()
    
    # 测试Hyperliquid持仓信息
    hyperliquid_info = test_hyperliquid_positions()
    
    # 测试Telegram通知
    test_telegram_notifications(binance_info, hyperliquid_info)
    
    logger.info("")
    logger.info("=" * 80)
    logger.info("测试完成")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()

