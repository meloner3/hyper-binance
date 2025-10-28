"""
测试Hyperliquid持仓查询功能
"""
import logging
from logger_config import setup_logger
from hyperliquid_monitor import HyperliquidMonitor
from config import HYPERLIQUID_API_URL, MONITOR_ADDRESS, USER_FILLS_LIMIT

# 设置日志
setup_logger(log_file='test_position.log', log_level='INFO')
logger = logging.getLogger(__name__)


def test_position_query():
    """测试持仓查询功能"""
    
    logger.info("=" * 80)
    logger.info("测试Hyperliquid持仓查询功能")
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
        
        # 1. 测试API接口 - 打印最近一笔订单
        monitor.print_latest_fill()
        logger.info("")
        
        # 2. 打印持仓信息
        monitor.print_positions()
        
        logger.info("")
        logger.info("=" * 80)
        logger.info("✅ 测试完成!")
        logger.info("=" * 80)
        
        return True
        
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
    print("测试Hyperliquid持仓查询功能")
    print("=" * 80)
    print(f"监控地址: {MONITOR_ADDRESS}")
    print("=" * 80)
    print("\n开始测试...\n")
    
    success = test_position_query()
    
    if success:
        print("\n✅ 测试成功完成！")
    else:
        print("\n❌ 测试失败，请查看日志文件 test_position.log")

