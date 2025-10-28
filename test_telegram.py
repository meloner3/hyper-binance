"""
测试Telegram通知功能
"""
import logging
from logger_config import setup_logger
from telegram_notifier import TelegramNotifier
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, TELEGRAM_ENABLED

# 设置日志
setup_logger(log_file='test_telegram.log', log_level='INFO')
logger = logging.getLogger(__name__)


def test_telegram_notification():
    """测试Telegram通知功能"""
    
    logger.info("=" * 80)
    logger.info("测试Telegram通知功能")
    logger.info("=" * 80)
    
    try:
        # 初始化通知器
        logger.info(f"初始化Telegram通知器...")
        logger.info(f"启用状态: {TELEGRAM_ENABLED}")
        logger.info(f"Bot Token: {TELEGRAM_BOT_TOKEN[:20]}..." if TELEGRAM_BOT_TOKEN != 'your_telegram_bot_token_here' else "未配置")
        logger.info(f"Chat ID: {TELEGRAM_CHAT_ID}")
        
        notifier = TelegramNotifier(
            bot_token=TELEGRAM_BOT_TOKEN,
            chat_id=TELEGRAM_CHAT_ID,
            enabled=TELEGRAM_ENABLED
        )
        
        if not notifier.enabled:
            logger.warning("⚠️  Telegram通知未启用或配置不正确")
            logger.info("")
            logger.info("请在 config.py 中配置:")
            logger.info("1. TELEGRAM_ENABLED = True")
            logger.info("2. TELEGRAM_BOT_TOKEN = 'your_bot_token'")
            logger.info("3. TELEGRAM_CHAT_ID = 'your_chat_id'")
            logger.info("")
            logger.info("如何获取:")
            logger.info("1. Bot Token: 通过 @BotFather 创建机器人获取")
            logger.info("2. Chat ID: 发送消息给机器人后，访问:")
            logger.info("   https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates")
            return False
        
        logger.info("✅ Telegram通知器初始化成功")
        logger.info("")
        
        # 测试连接
        logger.info("测试Telegram连接...")
        success = notifier.test_connection()
        
        if success:
            logger.info("")
            logger.info("=" * 80)
            logger.info("✅ 测试完成! Telegram通知功能正常")
            logger.info("=" * 80)
            logger.info("")
            logger.info("请检查您的Telegram，应该收到一条测试消息")
            return True
        else:
            logger.error("")
            logger.error("=" * 80)
            logger.error("❌ 测试失败! Telegram通知功能异常")
            logger.error("=" * 80)
            logger.error("")
            logger.error("可能的原因:")
            logger.error("1. Bot Token 不正确")
            logger.error("2. Chat ID 不正确")
            logger.error("3. 网络连接问题")
            logger.error("4. 未与机器人开始对话")
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
    print("测试Telegram通知功能")
    print("=" * 80)
    print("\n开始测试...\n")
    
    success = test_telegram_notification()
    
    if success:
        print("\n✅ 测试成功完成！请检查Telegram消息")
    else:
        print("\n❌ 测试失败，请查看日志文件 test_telegram.log")
        print("\n配置帮助:")
        print("1. 创建Telegram机器人: 与 @BotFather 对话，使用 /newbot 命令")
        print("2. 获取Bot Token: BotFather会提供")
        print("3. 获取Chat ID:")
        print("   - 向机器人发送任意消息")
        print("   - 访问: https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates")
        print("   - 在返回的JSON中找到 'chat' -> 'id'")

