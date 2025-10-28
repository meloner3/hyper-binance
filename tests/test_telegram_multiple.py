"""
测试 Telegram 连续发送多条消息
用于验证事件循环错误是否已修复
"""
import logging
import time
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, TELEGRAM_ENABLED
from logger_config import setup_logger
from telegram_notifier import TelegramNotifier

# 设置日志
setup_logger(log_file='test_telegram_multiple.log', log_level='INFO')
logger = logging.getLogger(__name__)


def test_single_message():
    """测试发送单条消息"""
    logger.info("=" * 60)
    logger.info("测试1: 发送单条消息")
    logger.info("=" * 60)
    
    notifier = TelegramNotifier(
        bot_token=TELEGRAM_BOT_TOKEN,
        chat_id=TELEGRAM_CHAT_ID,
        enabled=TELEGRAM_ENABLED
    )
    
    if not notifier.enabled:
        logger.warning("Telegram 通知未启用，跳过测试")
        return False
    
    result = notifier.send_message("🧪 测试消息：单条消息发送")
    logger.info(f"结果: {'✅ 成功' if result else '❌ 失败'}")
    return result


def test_multiple_messages_fast():
    """测试快速连续发送多条消息"""
    logger.info("")
    logger.info("=" * 60)
    logger.info("测试2: 快速连续发送5条消息（无延迟）")
    logger.info("=" * 60)
    
    notifier = TelegramNotifier(
        bot_token=TELEGRAM_BOT_TOKEN,
        chat_id=TELEGRAM_CHAT_ID,
        enabled=TELEGRAM_ENABLED
    )
    
    if not notifier.enabled:
        logger.warning("Telegram 通知未启用，跳过测试")
        return False
    
    success_count = 0
    fail_count = 0
    
    for i in range(5):
        logger.info(f"发送消息 {i+1}/5...")
        result = notifier.send_message(f"🧪 测试消息 {i+1}/5：快速连续发送")
        
        if result:
            success_count += 1
            logger.info(f"  ✅ 消息 {i+1} 发送成功")
        else:
            fail_count += 1
            logger.error(f"  ❌ 消息 {i+1} 发送失败")
    
    logger.info("")
    logger.info(f"结果统计: 成功 {success_count}, 失败 {fail_count}")
    return fail_count == 0


def test_multiple_messages_slow():
    """测试缓慢连续发送多条消息（有延迟）"""
    logger.info("")
    logger.info("=" * 60)
    logger.info("测试3: 缓慢连续发送5条消息（间隔1秒）")
    logger.info("=" * 60)
    
    notifier = TelegramNotifier(
        bot_token=TELEGRAM_BOT_TOKEN,
        chat_id=TELEGRAM_CHAT_ID,
        enabled=TELEGRAM_ENABLED
    )
    
    if not notifier.enabled:
        logger.warning("Telegram 通知未启用，跳过测试")
        return False
    
    success_count = 0
    fail_count = 0
    
    for i in range(5):
        logger.info(f"发送消息 {i+1}/5...")
        result = notifier.send_message(f"🧪 测试消息 {i+1}/5：缓慢连续发送")
        
        if result:
            success_count += 1
            logger.info(f"  ✅ 消息 {i+1} 发送成功")
        else:
            fail_count += 1
            logger.error(f"  ❌ 消息 {i+1} 发送失败")
        
        if i < 4:  # 最后一条不需要等待
            logger.info("  等待1秒...")
            time.sleep(1)
    
    logger.info("")
    logger.info(f"结果统计: 成功 {success_count}, 失败 {fail_count}")
    return fail_count == 0


def test_startup_simulation():
    """模拟启动时的消息发送"""
    logger.info("")
    logger.info("=" * 60)
    logger.info("测试4: 模拟启动时的消息发送")
    logger.info("=" * 60)
    
    notifier = TelegramNotifier(
        bot_token=TELEGRAM_BOT_TOKEN,
        chat_id=TELEGRAM_CHAT_ID,
        enabled=TELEGRAM_ENABLED
    )
    
    if not notifier.enabled:
        logger.warning("Telegram 通知未启用，跳过测试")
        return False
    
    # 模拟启动通知
    logger.info("发送启动通知...")
    result1 = notifier.send_message(
        "🤖 <b>系统启动通知（测试）</b>\n\n"
        "⏰ 启动时间: 2025-10-28 14:00:00\n"
        "✅ 系统已启动，开始监控..."
    )
    logger.info(f"  启动通知: {'✅ 成功' if result1 else '❌ 失败'}")
    
    # 模拟账户信息
    logger.info("发送账户信息...")
    result2 = notifier.send_message(
        "💼 <b>币安合约账户信息（测试）</b>\n\n"
        "💰 <b>账户余额:</b>\n"
        "• USDT: 1,000.00\n"
        "📊 <b>当前持仓:</b>\n"
        "• 当前无持仓"
    )
    logger.info(f"  账户信息: {'✅ 成功' if result2 else '❌ 失败'}")
    
    # 模拟持仓信息
    logger.info("发送持仓信息...")
    result3 = notifier.send_message(
        "📊 <b>监控地址持仓信息（测试）</b>\n\n"
        "💼 <b>账户总览:</b>\n"
        "• 账户价值: $10,000.00\n"
        "• 已用保证金: $0.00\n"
        "• 可用余额: $10,000.00\n"
        "📈 <b>当前持仓:</b>\n"
        "• 当前无持仓"
    )
    logger.info(f"  持仓信息: {'✅ 成功' if result3 else '❌ 失败'}")
    
    all_success = result1 and result2 and result3
    logger.info("")
    logger.info(f"总体结果: {'✅ 全部成功' if all_success else '❌ 部分失败'}")
    return all_success


def main():
    """主测试函数"""
    logger.info("\n🧪 开始 Telegram 多消息发送测试\n")
    
    results = {
        '单条消息': test_single_message(),
        '快速连续消息': test_multiple_messages_fast(),
        '缓慢连续消息': test_multiple_messages_slow(),
        '启动模拟': test_startup_simulation()
    }
    
    logger.info("")
    logger.info("=" * 60)
    logger.info("测试总结")
    logger.info("=" * 60)
    
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        logger.info(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    logger.info("")
    logger.info("=" * 60)
    if all_passed:
        logger.info("🎉 所有测试通过！事件循环错误已修复。")
    else:
        logger.error("⚠️  部分测试失败，请检查错误日志。")
    logger.info("=" * 60)
    logger.info("")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n测试被用户中断")
    except Exception as e:
        logger.error(f"\n测试过程中发生错误: {e}", exc_info=True)

