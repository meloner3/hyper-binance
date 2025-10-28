"""
测试 Hyperliquid WebSocket 连接稳定性
运行5分钟，监控连接状态和心跳情况
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

# 设置日志为DEBUG级别以查看心跳信息
setup_logger(log_file='test_websocket_stability.log', log_level='DEBUG')
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
    logger.info("🧪 测试 Hyperliquid WebSocket 连接稳定性")
    logger.info("=" * 80)
    logger.info(f"监控地址: {MONITOR_ADDRESS}")
    logger.info(f"WebSocket URL: {HYPERLIQUID_WS_URL}")
    logger.info(f"测试时长: 5分钟")
    logger.info(f"心跳间隔: 20秒")
    logger.info("")
    
    # 创建监控器
    monitor = HyperliquidMonitorWS(
        api_url=HYPERLIQUID_API_URL,
        ws_url=HYPERLIQUID_WS_URL,
        monitor_address=MONITOR_ADDRESS
    )
    
    try:
        # 启动监控（测试5分钟）
        logger.info("启动WebSocket监控，将运行5分钟...")
        logger.info("监控重点：")
        logger.info("  1. 连接是否会在60秒左右断开")
        logger.info("  2. 心跳机制是否正常工作")
        logger.info("  3. 重连机制是否有效")
        logger.info("")
        
        # 记录开始时间
        start_time = time.time()
        test_duration = 300  # 5分钟
        
        # 启动监控（在后台线程运行）
        import threading
        monitor_thread = threading.Thread(
            target=monitor.start_monitoring,
            kwargs={
                'callback': test_callback,
                'position_print_interval': 120  # 2分钟打印一次持仓
            }
        )
        monitor_thread.daemon = True
        monitor_thread.start()
        
        # 主循环：每30秒打印一次状态
        last_report_time = start_time
        report_interval = 30  # 每30秒报告一次
        
        while time.time() - start_time < test_duration:
            time.sleep(5)
            current_time = time.time()
            
            # 每30秒打印一次详细状态
            if current_time - last_report_time >= report_interval:
                elapsed = int(current_time - start_time)
                remaining = int(test_duration - (current_time - start_time))
                
                logger.info("")
                logger.info("=" * 80)
                logger.info(f"⏱️  已运行: {elapsed}秒 | 剩余: {remaining}秒")
                logger.info(f"🔌 连接状态: {'已连接' if monitor.ws_connected else '已断开'}")
                logger.info(f"📊 统计信息:")
                logger.info(f"   - 总消息数: {monitor.ws_message_count}")
                logger.info(f"   - 收到订单: {monitor.fills_received_count}")
                logger.info(f"   - Ping次数: {monitor.ping_count}")
                logger.info(f"   - Pong次数: {monitor.pong_count}")
                logger.info(f"   - 错误次数: {monitor.ws_error_count}")
                logger.info(f"   - 重连次数: {monitor.reconnect_count}")
                
                # 检查心跳健康状态
                if monitor.last_pong_time > 0:
                    time_since_last_pong = current_time - monitor.last_pong_time
                    logger.info(f"   - 上次Pong: {time_since_last_pong:.1f}秒前")
                    if time_since_last_pong > 40:
                        logger.warning(f"   ⚠️  警告: 超过40秒未收到Pong响应！")
                
                logger.info("=" * 80)
                logger.info("")
                
                last_report_time = current_time
        
        # 测试完成
        logger.info("")
        logger.info("=" * 80)
        logger.info("✅ 测试完成！")
        logger.info("=" * 80)
        logger.info(f"📊 最终统计:")
        logger.info(f"   - 运行时长: {test_duration}秒 ({test_duration//60}分钟)")
        logger.info(f"   - 总消息数: {monitor.ws_message_count}")
        logger.info(f"   - 收到订单: {monitor.fills_received_count}")
        logger.info(f"   - Ping次数: {monitor.ping_count}")
        logger.info(f"   - Pong次数: {monitor.pong_count}")
        logger.info(f"   - 错误次数: {monitor.ws_error_count}")
        logger.info(f"   - 重连次数: {monitor.reconnect_count}")
        logger.info("")
        
        # 评估结果
        if monitor.reconnect_count == 0:
            logger.info("✅ 优秀！连接保持稳定，没有发生重连")
        elif monitor.reconnect_count <= 2:
            logger.info("✅ 良好！连接基本稳定，仅发生少量重连")
        else:
            logger.warning(f"⚠️  需要关注：发生了 {monitor.reconnect_count} 次重连")
        
        if monitor.ws_error_count == 0:
            logger.info("✅ 没有错误发生")
        else:
            logger.warning(f"⚠️  发生了 {monitor.ws_error_count} 次错误")
        
        logger.info("=" * 80)
        
        # 停止监控
        monitor.stop()
        
    except KeyboardInterrupt:
        logger.info("")
        logger.info("用户中断测试")
        monitor.stop()
    except Exception as e:
        logger.error(f"测试失败: {e}", exc_info=True)
        monitor.stop()


if __name__ == "__main__":
    main()

