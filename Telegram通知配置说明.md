## Telegram通知功能配置说明

## 📱 功能概述

系统支持通过Telegram机器人发送实时通知，包括：

1. ✅ **系统启动通知** - 程序启动时发送配置信息
2. ✅ **平仓检测警报** - 检测到平多仓操作时立即通知
3. ✅ **交易成功通知** - 开空单成功后发送交易详情
4. ✅ **交易失败警报** - 交易失败时发送错误信息
5. ✅ **API测试结果** - 启动时API接口测试结果

## 🚀 快速开始

### 第1步：创建Telegram机器人

1. 在Telegram中搜索 `@BotFather`
2. 发送 `/newbot` 命令
3. 按提示设置机器人名称和用户名
4. 保存BotFather返回的 **Bot Token**

示例：
```
Use this token to access the HTTP API:
1234567890:ABCdefGHIjklMNOpqrsTUVwxyz1234567890
```

### 第2步：获取Chat ID

1. 向您创建的机器人发送任意消息（如 `/start`）
2. 在浏览器中访问以下URL（替换YOUR_BOT_TOKEN）：
```
https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
```

3. 在返回的JSON中找到 `chat` -> `id`

示例返回：
```json
{
  "ok": true,
  "result": [{
    "message": {
      "chat": {
        "id": 123456789,  // 这就是您的Chat ID
        "first_name": "Your Name",
        "type": "private"
      }
    }
  }]
}
```

### 第3步：配置config.py

编辑 `config.py` 文件，填入您的配置：

```python
# Telegram通知配置
TELEGRAM_ENABLED = True  # 启用Telegram通知
TELEGRAM_BOT_TOKEN = '1234567890:ABCdefGHIjklMNOpqrsTUVwxyz1234567890'  # 您的Bot Token
TELEGRAM_CHAT_ID = '123456789'  # 您的Chat ID
```

### 第4步：测试配置

运行测试脚本：

```bash
python test_telegram.py
```

如果配置正确，您应该在Telegram中收到一条测试消息。

## 📋 通知消息示例

### 1. 系统启动通知

```
🤖 系统启动通知

⏰ 启动时间: 2025-10-28 13:00:00

📋 配置信息:
• 监控地址: 0xc2a30212...994E5f2
• 扫描间隔: 1秒
• 杠杆倍数: 100x
• 保证金: 1000 USDC
• 持仓价值: 100000 USDC
• 交易对: ETH→ETHUSDC, BTC→BTCUSDC

✅ 系统已启动，开始监控...
```

### 2. 平仓检测警报

```
🚨 检测到平多仓操作！

📊 交易信息:
• 币种: BTC
• 数量: 10.5
• 价格: $113,875.90
• 已实现盈亏: 💰 $125,000.00
• 时间: 2025-10-28 12:45:30

⚡️ 准备在币安开空单...
```

### 3. 交易成功通知

```
✅ 开空单成功！

💼 交易详情:
• 币种: BTC (BTCUSDC)
• 订单ID: 12345678
• 杠杆: 100x
• 保证金: $1,000.00
• 持仓价值: $100,000.00
• 数量: 0.878
• 入场价格: $113,876.50

📈 持仓已建立，请注意风险管理！
```

### 4. 交易失败警报

```
❌ 开空单失败！

• 币种: BTC
• 错误信息: 开空单失败，请查看日志
• 时间: 2025-10-28 12:46:00

⚠️ 请检查系统日志了解详情
```

## ⚙️ 配置选项

### 启用/禁用通知

```python
# 启用通知
TELEGRAM_ENABLED = True

# 禁用通知
TELEGRAM_ENABLED = False
```

### 通知到多个用户

如果需要通知多个用户，可以：

1. **方法1**：创建Telegram群组
   - 创建一个群组
   - 将机器人添加到群组
   - 获取群组的Chat ID（通常是负数）

2. **方法2**：修改代码支持多个Chat ID
   - 在 `config.py` 中配置多个Chat ID
   - 修改 `telegram_notifier.py` 循环发送

## 🔧 故障排查

### 问题1：未收到测试消息

**可能原因**：
- Bot Token 不正确
- Chat ID 不正确
- 未与机器人开始对话

**解决方案**：
1. 确认Bot Token和Chat ID正确
2. 向机器人发送 `/start` 命令
3. 重新运行测试脚本

### 问题2：提示"Telegram通知未启用"

**可能原因**：
- `TELEGRAM_ENABLED = False`
- Bot Token 或 Chat ID 未配置

**解决方案**：
1. 检查 `config.py` 中的配置
2. 确保 `TELEGRAM_ENABLED = True`
3. 确保填入了正确的Token和Chat ID

### 问题3：发送失败

**可能原因**：
- 网络连接问题
- Telegram服务器不可用
- 机器人被封禁

**解决方案**：
1. 检查网络连接
2. 尝试访问 https://telegram.org 确认服务可用
3. 检查机器人状态

### 问题4：Chat ID 获取失败

**解决方案**：
1. 确保已向机器人发送消息
2. 使用正确的Bot Token访问getUpdates接口
3. 如果返回为空，尝试再次发送消息

## 📱 高级配置

### 自定义消息格式

可以修改 `telegram_notifier.py` 中的消息模板：

```python
def send_startup_message(self, monitor_address: str, config_info: dict):
    message = f"""
🤖 <b>自定义启动消息</b>
...
"""
    self.send_message(message)
```

### 添加新的通知类型

在 `telegram_notifier.py` 中添加新方法：

```python
def send_custom_alert(self, title: str, content: str):
    """发送自定义警报"""
    message = f"""
⚠️ <b>{title}</b>

{content}
"""
    self.send_message(message)
```

### 消息格式

支持HTML格式：
- `<b>粗体</b>`
- `<i>斜体</i>`
- `<code>代码</code>`
- `<a href="url">链接</a>`

## 🔒 安全建议

1. **保护Bot Token**
   - 不要将Token提交到代码仓库
   - 不要在公开场合分享Token
   - 定期更换Token

2. **限制机器人权限**
   - 在BotFather中禁用不需要的功能
   - 只添加信任的用户到通知列表

3. **监控使用情况**
   - 定期检查发送计数
   - 注意异常的发送行为

## 📊 统计信息

程序会自动统计：
- 总发送次数：`notifier.send_count`
- 错误次数：`notifier.error_count`

可以在日志中查看这些统计信息。

## 🧪 测试命令

```bash
# 测试Telegram连接
python test_telegram.py

# 查看测试日志
cat test_telegram.log
```

## 📚 参考资源

- [Telegram Bot API文档](https://core.telegram.org/bots/api)
- [BotFather使用指南](https://core.telegram.org/bots#6-botfather)
- [python-telegram-bot文档](https://python-telegram-bot.readthedocs.io/)

## ❓ 常见问题

### Q: 机器人可以主动发消息吗？
A: 是的，但用户必须先向机器人发送消息（如 `/start`）。

### Q: 支持发送图片吗？
A: 当前版本只支持文本消息，如需图片可以扩展代码。

### Q: 消息有长度限制吗？
A: Telegram单条消息最长4096个字符。

### Q: 可以撤回消息吗？
A: 可以，需要保存message_id并调用相应API。

### Q: 支持按钮和键盘吗？
A: 可以扩展代码添加InlineKeyboard或ReplyKeyboard。

## 💡 使用建议

1. **首次使用**：先运行测试脚本确认配置正确
2. **生产环境**：建议创建专用的通知群组
3. **消息频率**：避免过于频繁的通知
4. **重要通知**：可以添加特殊标记或emoji
5. **日志备份**：Telegram通知是补充，不能替代日志

## 🎯 下一步

配置完成后：
1. ✅ 运行 `python test_telegram.py` 测试
2. ✅ 运行 `python main.py` 启动主程序
3. ✅ 检查Telegram接收启动通知
4. ✅ 等待交易触发，验证通知功能

祝您使用愉快！🚀

