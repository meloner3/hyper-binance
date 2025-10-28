# 快速开始指南

本指南将帮助你快速设置和运行 Hyperliquid 监控交易机器人。

## 前置要求

- Python 3.8 或更高版本
- 币安账户和 API 密钥
- Telegram 账户（用于接收通知）

## 5 分钟快速设置

### 1. 安装依赖 (1分钟)

```bash
cd /Users/meloner/pythoncode2/hypegendan
pip install -r requirements.txt
```

### 2. 配置文件 (2分钟)

```bash
# 复制配置模板
cp config.example.py config.py

# 编辑配置文件
nano config.py  # 或使用你喜欢的编辑器
```

**必须配置的项目：**

```python
# 币安 API（必填）
BINANCE_API_KEY = 'your_binance_api_key_here'
BINANCE_API_SECRET = 'your_binance_api_secret_here'

# Telegram 通知（可选但推荐）
TELEGRAM_ENABLED = True
TELEGRAM_BOT_TOKEN = 'your_telegram_bot_token_here'
TELEGRAM_CHAT_ID = 'your_telegram_chat_id_here'

# 监控地址
MONITOR_ADDRESS = '0xYourHyperliquidAddressHere'
```

**如何获取 Telegram Bot Token？**
查看 [docs/Telegram通知配置说明.md](docs/Telegram通知配置说明.md)

### 3. 测试配置 (1分钟)

```bash
# 测试 Telegram 通知
python tests/test_telegram.py

# 测试 Hyperliquid 连接
python tests/test_fills.py
```

### 4. 启动程序 (1分钟)

```bash
python main.py
```

## 首次运行检查清单

启动后，你应该看到：

- ✅ 系统启动信息
- ✅ 开单状态记录
- ✅ 币安账户余额
- ✅ Telegram 收到启动通知（如果启用）
- ✅ Telegram 收到账户信息（如果启用）
- ✅ Telegram 收到持仓信息（如果启用）
- ✅ 开始监控日志

## 常见问题快速解决

### Q1: 导入错误 - ModuleNotFoundError

```bash
pip install -r requirements.txt
```

### Q2: 币安 API 连接失败

检查：
1. API 密钥是否正确
2. API 权限是否包含合约交易
3. IP 白名单设置

### Q3: Telegram 通知不工作

检查：
1. Bot Token 是否正确
2. Chat ID 是否正确
3. `TELEGRAM_ENABLED` 是否为 `True`

运行测试：
```bash
python tests/test_telegram.py
```

### Q4: 没有检测到平仓

可能原因：
1. 监控地址没有交易活动
2. 监控地址配置错误
3. 扫描间隔设置过大

## 安全建议

### 测试网先行

**强烈建议先在测试网测试！**

```python
# 在 config.py 中设置
USE_TESTNET = True
```

测试网地址：https://testnet.binancefuture.com

### API 密钥安全

1. ✅ 不要将 `config.py` 提交到代码仓库
2. ✅ 设置 IP 白名单
3. ✅ 只授予必要的权限
4. ✅ 定期更换 API 密钥

### 风险控制

1. ✅ 从小额开始测试
2. ✅ 设置合理的杠杆倍数
3. ✅ 监控账户余额
4. ✅ 定期检查持仓

## 下一步

### 了解功能

1. [开单状态管理](docs/开单状态管理说明.md) - 防止重复开单
2. [启动推送功能](docs/启动推送说明.md) - 自动推送账户信息
3. [持仓监控](docs/持仓监控说明.md) - 定时显示持仓状态

### 管理工具

```bash
# 查看和重置开单状态
python reset_trade_state.py
```

### 查看日志

```bash
# 实时查看日志
tail -f trading_monitor.log

# 查看最近 100 行
tail -n 100 trading_monitor.log
```

## 使用流程

### 日常使用

```
1. 启动程序
   python main.py

2. 查看 Telegram 通知
   - 确认启动成功
   - 查看账户信息
   - 查看持仓信息

3. 监控运行
   - 程序会自动监控和交易
   - 收到 Telegram 通知时查看
   - 定期检查日志

4. 平仓后重置状态
   python reset_trade_state.py
   选择重置对应币种
```

### 停止程序

```bash
# 按 Ctrl+C 停止
# 或发送 SIGTERM 信号
kill -TERM <pid>
```

## 监控建议

### 日志监控

```bash
# 查看错误日志
grep ERROR trading_monitor.log

# 查看开单记录
grep "成功在币安开空" trading_monitor.log

# 查看跳过的开单
grep "已经开过单" trading_monitor.log
```

### 定期检查

- 每天检查账户余额
- 每天检查持仓状态
- 每周检查开单状态
- 定期备份 `trade_state.json`

## 性能优化

### 扫描间隔

```python
# 在 config.py 中调整
SCAN_INTERVAL = 10  # 秒，建议 5-30 秒
```

### 持仓打印间隔

```python
# 在 config.py 中调整
POSITION_PRINT_INTERVAL = 300  # 秒，建议 300-600 秒
```

## 故障排除

### 程序崩溃

1. 查看日志文件 `trading_monitor.log`
2. 查看错误信息
3. 检查网络连接
4. 检查 API 密钥是否有效

### 重复开单

如果发现重复开单：

1. 立即停止程序
2. 检查 `trade_state.json` 文件
3. 手动平仓（如需要）
4. 重置开单状态
5. 重新启动程序

### 通知不及时

可能原因：
1. Telegram 服务器延迟
2. 网络连接问题
3. 扫描间隔设置过大

## 获取帮助

### 文档

- [完整文档](docs/README.md)
- [常见问题](README.md#常见问题)
- [更新日志](CHANGELOG.md)

### 测试

```bash
# 运行所有测试
./run_all_tests.sh

# 或单独运行测试
python tests/test_telegram.py
```

### 社区

- 提交 Issue
- 查看现有 Issue
- 参与讨论

## 重要提醒

⚠️ **风险警告**

1. 加密货币交易具有高风险
2. 使用高杠杆可能导致快速爆仓
3. 本程序仅供学习和研究使用
4. 使用者需自行承担所有风险
5. 不要投入超过你能承受损失的资金

✅ **最佳实践**

1. 先在测试网充分测试
2. 从小额开始
3. 设置合理的止损
4. 定期检查和监控
5. 保持 API 密钥安全

---

**准备好了吗？**

```bash
# 开始你的交易机器人之旅！
python main.py
```

祝交易顺利！🚀

