"""
配置文件示例
复制此文件为 config.py 并填入你的实际配置
"""

# Binance API配置
BINANCE_API_KEY = 'your_binance_api_key_here'
BINANCE_API_SECRET = 'your_binance_api_secret_here'

# 监控配置
MONITOR_ADDRESS = '0xc2a30212a8DdAc9e123944d6e29FADdCe994E5f2'
SCAN_INTERVAL = 5  # 扫描间隔（秒） - 仅用于HTTP轮询模式
USE_WEBSOCKET = True  # 是否使用WebSocket模式（推荐，避免速率限制）
POSITION_PRINT_INTERVAL = 300  # 持仓打印间隔（秒），默认300秒=5分钟
USER_FILLS_LIMIT = 20  # 每次获取的订单数量，默认20条（仅HTTP轮询模式使用）

# 交易配置
LEVERAGE = 100  # 杠杆倍数
POSITION_SIZE_USDC = 50  # 保证金金额（USDC），实际持仓价值 = 保证金 × 杠杆

# Hyperliquid API配置
HYPERLIQUID_API_URL = 'https://api.hyperliquid.xyz/info'
HYPERLIQUID_WS_URL = 'wss://api.hyperliquid.xyz/ws'  # WebSocket地址
# WebSocket心跳间隔：20秒（自动发送ping保持连接，防止超时断开）

# 交易对配置
TRADING_PAIRS = {
    'ETH': 'ETHUSDC',
    'BTC': 'BTCUSDC'
}

# 日志配置
LOG_FILE = 'trading_monitor.log'
LOG_LEVEL = 'INFO'

# 测试模式（True=使用币安测试网，False=使用正式网）
USE_TESTNET = False

# Telegram通知配置
TELEGRAM_ENABLED = True  # 是否启用Telegram通知
TELEGRAM_BOT_TOKEN = 'your_telegram_bot_token_here'  # Telegram Bot Token
TELEGRAM_CHAT_ID = 'your_telegram_chat_id_here'  # 接收消息的Chat ID

