"""
测试Hyperliquid订单查询功能
"""
import logging
from logger_config import setup_logger
from hyperliquid_monitor import HyperliquidMonitor
from config import HYPERLIQUID_API_URL, MONITOR_ADDRESS, USER_FILLS_LIMIT

# 设置日志
setup_logger(log_file='test_fills.log', log_level='INFO')
logger = logging.getLogger(__name__)


def test_fills_query():
    """测试订单查询功能"""
    
    logger.info("=" * 80)
    logger.info("测试Hyperliquid订单查询功能")
    logger.info("=" * 80)
    
    try:
        # 初始化监控器
        logger.info(f"初始化监控器...")
        logger.info(f"API地址: {HYPERLIQUID_API_URL}")
        logger.info(f"监控地址: {MONITOR_ADDRESS}")
        
        monitor = HyperliquidMonitor(
            api_url=HYPERLIQUID_API_URL,
            monitor_address=MONITOR_ADDRESS,
            user_fills_limit=USER_FILLS_LIMIT
        )
        
        logger.info("✅ 监控器初始化成功")
        logger.info("")
        
        # 测试API接口
        success = monitor.print_latest_fill()
        
        if success:
            logger.info("")
            logger.info("=" * 80)
            logger.info("✅ 测试完成! API接口正常")
            logger.info("=" * 80)
            return True
        else:
            logger.error("")
            logger.error("=" * 80)
            logger.error("❌ 测试失败! API接口异常")
            logger.error("=" * 80)
            return False
        
    except Exception as e:
        logger.error("")
        logger.error("=" * 80)
        logger.error(f"❌ 测试失败: {e}")
        logger.error("=" * 80)
        import traceback
        logger.error(traceback.format_exc())
        return False


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("测试Hyperliquid订单查询功能")
    print("=" * 80)
    print(f"监控地址: {MONITOR_ADDRESS}")
    print("=" * 80)
    print("\n开始测试...\n")
    
    success = test_fills_query()
    
    if success:
        print("\n✅ 测试成功完成！API接口正常工作")
    else:
        print("\n❌ 测试失败，请查看日志文件 test_fills.log")

