"""
测试 Hyperliquid WebSocket 连接
"""
import sys
import os
import time
import logging

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import MONITOR_ADDRESS, HYPERLIQUID_API_URL, HYPERLIQUID_WS_URL
from logger_config import setup_logger
from hyperliquid_monitor_ws import HyperliquidMonitorWS

# 设置日志
setup_logger(log_file='test_websocket.log', log_level='INFO')
logger = logging.getLogger(__name__)


def test_callback(position):
    """测试回调函数"""
    logger.info("=" * 80)
    logger.info("🎯 回调函数被触发！")
    logger.info(f"检测到平多仓: {position}")
    logger.info("=" * 80)


def main():
    """主测试函数"""
    logger.info("=" * 80)
    logger.info("🧪 测试 Hyperliquid WebSocket 连接")
    logger.info("=" * 80)
    logger.info(f"监控地址: {MONITOR_ADDRESS}")
    logger.info(f"WebSocket URL: {HYPERLIQUID_WS_URL}")
    logger.info("")
    
    # 创建监控器
    monitor = HyperliquidMonitorWS(
        api_url=HYPERLIQUID_API_URL,
        ws_url=HYPERLIQUID_WS_URL,
        monitor_address=MONITOR_ADDRESS
    )
    
    try:
        # 启动监控（测试30秒）
        logger.info("启动WebSocket监控，将运行30秒...")
        logger.info("如果在此期间有新的订单成交，将会实时收到通知")
        logger.info("")
        
        # 启动监控
        monitor.start_monitoring(
            callback=test_callback,
            position_print_interval=60  # 1分钟打印一次持仓
        )
        
        # 等待30秒
        time.sleep(30)
        
        # 停止监控
        monitor.stop()
        
        logger.info("")
        logger.info("=" * 80)
        logger.info("✅ 测试完成")
        logger.info(f"统计信息:")
        logger.info(f"  WebSocket消息总数: {monitor.ws_message_count}")
        logger.info(f"  收到的订单数: {monitor.fills_received_count}")
        logger.info(f"  错误次数: {monitor.ws_error_count}")
        logger.info("=" * 80)
        
    except KeyboardInterrupt:
        logger.info("用户中断测试")
        monitor.stop()
    except Exception as e:
        logger.error(f"测试失败: {e}", exc_info=True)
        monitor.stop()


if __name__ == "__main__":
    main()

