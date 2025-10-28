# Hyperliquid监控交易机器人

这是一个自动监控Hyperliquid交易所特定地址的交易行为，并在检测到平多仓操作时自动在币安开空单的交易机器人。

> 📖 **快速开始**: 查看 [QUICKSTART.md](QUICKSTART.md) 快速设置和运行
> 
> 📚 **完整文档**: 查看 [docs/](docs/) 目录获取详细文档

## 功能特性

- 🔍 实时监控Hyperliquid指定地址的交易订单
- 📊 自动检测ETH和BTC的平多仓操作
- 🤖 自动在币安交易所开空单
- 📝 完整的日志记录和错误处理
- ⚙️ 可配置的杠杆倍数和持仓量
- 📱 Telegram通知功能（启动通知、交易通知）
- 💼 启动时自动推送账户余额和持仓信息
- 🔒 开单状态记录，防止重复开单

## 工作原理

1. 每秒调用Hyperliquid的`user_fills`接口扫描指定地址的历史订单
2. 检测是否有平多仓操作（卖出且有已实现盈亏的订单）
3. 如果检测到ETH或BTC的平多仓，立即调用币安API开空单
4. 使用100x杠杆，持仓量10000 USDC
5. 交易对为BTCUSDC和ETHUSDC

## 安装步骤

### 1. 克隆项目

```bash
cd /Users/meloner/pythoncode2/hypegendan
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置文件设置

复制配置文件模板：

```bash
cp config.example.py config.py
```

编辑`config.py`文件，填入你的币安API密钥和其他配置：

```python
# Binance API配置
BINANCE_API_KEY = 'your_binance_api_key_here'  # 填入你的API密钥
BINANCE_API_SECRET = 'your_binance_api_secret_here'  # 填入你的API密钥

# 监控配置
MONITOR_ADDRESS = '0xc2a30212a8DdAc9e123944d6e29FADdCe994E5f2'
SCAN_INTERVAL = 1  # 扫描间隔（秒）

# 交易配置
LEVERAGE = 100  # 杠杆倍数
POSITION_SIZE_USDC = 10000  # 持仓量（USDC）

# 测试模式（True=使用币安测试网，False=使用正式网）
USE_TESTNET = False
```

## 使用方法

### 启动机器人

```bash
python main.py
```

### 停止机器人

按 `Ctrl+C` 停止监控

### 运行测试

所有测试脚本都在 `tests/` 目录中：

```bash
# 测试 Telegram 通知
python tests/test_telegram.py

# 测试 Telegram 多消息发送
python tests/test_telegram_multiple.py

# 测试启动推送功能
python tests/test_startup_notification.py

# 测试 Hyperliquid 订单接口
python tests/test_fills.py

# 测试 Hyperliquid 持仓查询
python tests/test_position.py

# 测试币安开单功能（⚠️ 会实际开单）
python tests/test_order.py
```

详细测试说明请查看 [tests/README.md](tests/README.md)

### 管理开单状态

```bash
python reset_trade_state.py
```

## 开单状态管理

为防止重复开单，系统会记录每个币种的开单状态。当检测到平仓信号并成功开单后，会标记该币种为"已开单"状态。如果再次检测到相同币种的平仓信号，系统会自动跳过，避免重复开单。

### 主要功能

1. **自动记录开单状态** - 开单成功后自动标记
2. **防止重复开单** - 检测到已开单的币种会跳过
3. **状态持久化** - 状态保存在文件中，程序重启后保留
4. **状态管理工具** - 提供交互式工具重置状态

### 使用场景

- 在币安手动平仓后，需要重置对应币种的状态
- 测试完成后重置所有状态
- 查看当前哪些币种已经开过单

详细说明请查看 [docs/开单状态管理说明.md](docs/开单状态管理说明.md)

## 启动推送功能

程序启动后会自动推送以下信息到Telegram：

1. **系统启动通知** - 包含配置信息（监控地址、扫描间隔、杠杆倍数等）
2. **币安合约账户信息** - 包含账户余额和当前持仓详情
3. **监控地址持仓信息** - 包含Hyperliquid地址的持仓和账户总览

详细说明请查看 [docs/启动推送说明.md](docs/启动推送说明.md)

## 配置说明

### 配置文件参数 (config.py)

| 参数名 | 说明 | 默认值 |
|--------|------|--------|
| `BINANCE_API_KEY` | 币安API密钥 | 必填 |
| `BINANCE_API_SECRET` | 币安API密钥 | 必填 |
| `MONITOR_ADDRESS` | 要监控的Hyperliquid地址 | 0xc2a30212a8DdAc9e123944d6e29FADdCe994E5f2 |
| `SCAN_INTERVAL` | 扫描间隔（秒） | 1 |
| `POSITION_PRINT_INTERVAL` | 持仓打印间隔（秒） | 300 (5分钟) |
| `USER_FILLS_LIMIT` | 每次获取的订单数量 | 20 |
| `LEVERAGE` | 杠杆倍数 | 100 |
| `POSITION_SIZE_USDC` | 持仓量（USDC） | 10000 |
| `USE_TESTNET` | 是否使用测试网 | False |
| `TRADING_PAIRS` | 交易对映射 | {'ETH': 'ETHUSDC', 'BTC': 'BTCUSDC'} |

### 币安API权限要求

确保你的币安API密钥具有以下权限：
- ✅ 启用合约交易
- ✅ 读取权限
- ✅ 交易权限

⚠️ **安全提示**：
- 不要将`config.py`提交到代码仓库（已添加到.gitignore）
- 建议设置IP白名单
- 定期更换API密钥

## 项目结构

```
hypegendan/
├── main.py                      # 主程序入口
├── config.py                    # 配置文件（需自行创建，包含敏感信息）
├── config.example.py            # 配置文件模板
├── logger_config.py             # 日志配置
├── hyperliquid_monitor.py       # Hyperliquid监控模块
├── binance_trader.py            # 币安交易模块
├── telegram_notifier.py         # Telegram通知模块
├── reset_trade_state.py         # 开单状态管理工具
├── trade_state.json             # 开单状态文件（自动生成）
├── requirements.txt             # Python依赖
├── .gitignore                   # Git忽略文件
├── README.md                    # 项目说明
├── docs/                        # 文档目录
│   ├── README.md                # 文档索引
│   ├── 启动推送说明.md           # 启动推送功能详细说明
│   ├── 开单状态管理说明.md       # 开单状态管理详细说明
│   ├── Telegram通知配置说明.md   # Telegram配置说明
│   ├── Telegram事件循环修复说明.md # 事件循环错误修复
│   ├── API速率限制说明.md        # API速率限制说明
│   ├── 持仓监控说明.md           # 持仓监控功能说明
│   ├── 启动检查说明.md           # 启动检查流程说明
│   ├── 更新说明.md              # 项目更新历史
│   └── 更新日志_启动推送.md      # 启动推送功能更新日志
└── tests/                       # 测试脚本目录
    ├── README.md                # 测试说明
    ├── test_telegram.py         # Telegram基本功能测试
    ├── test_telegram_multiple.py # Telegram多消息测试
    ├── test_startup_notification.py # 启动推送测试
    ├── test_fills.py            # Hyperliquid订单接口测试
    ├── test_position.py         # Hyperliquid持仓查询测试
    └── test_order.py            # 币安开单功能测试
```

## 日志说明

程序运行时会生成日志文件`trading_monitor.log`，包含：
- 监控状态信息
- 检测到的平仓操作
- 执行的交易操作
- 错误和异常信息

日志文件会自动轮转，单个文件最大10MB，保留最近5个文件。

## 风险提示

⚠️ **重要警告**：

1. **高风险交易**：使用100x杠杆进行交易具有极高风险，可能导致快速爆仓
2. **市场风险**：加密货币市场波动剧烈，价格可能快速变化
3. **API风险**：确保API密钥安全，避免泄露
4. **测试建议**：建议先在币安测试网进行测试（设置`USE_TESTNET = True`）
5. **资金管理**：不要投入超过你能承受损失的资金

## 测试模式

如需在币安测试网测试，修改`config.py`：

```python
USE_TESTNET = True  # 使用测试网
```

币安测试网地址：https://testnet.binancefuture.com

## 常见问题

### 1. 如何获取币安API密钥？

登录币安账户 → API管理 → 创建API → 启用合约交易权限

### 2. 为什么没有检测到平仓？

- 检查监控地址是否正确
- 检查该地址是否有交易活动
- 查看日志文件了解详细信息

### 3. 交易失败怎么办？

- 检查API密钥权限
- 确认账户余额充足
- 查看日志中的错误信息

### 4. config.py文件在哪里？

需要手动复制`config.example.py`为`config.py`，然后填入你的实际配置。

## 免责声明

本项目仅供学习和研究使用。使用本程序进行实际交易的所有风险由使用者自行承担。作者不对任何直接或间接的损失负责。

## 许可证

MIT License
