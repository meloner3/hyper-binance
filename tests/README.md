# 测试脚本说明

本目录包含所有测试脚本，用于验证各个功能模块。

## 测试脚本列表

### 1. test_telegram.py
测试 Telegram 通知基本功能。

**用途：**
- 测试 Telegram Bot 连接
- 发送测试消息
- 验证配置是否正确

**运行方法：**
```bash
cd /Users/meloner/pythoncode2/hypegendan
python tests/test_telegram.py
```

### 2. test_telegram_multiple.py
测试 Telegram 连续发送多条消息。

**用途：**
- 验证事件循环错误是否已修复
- 测试快速连续发送消息
- 测试缓慢连续发送消息
- 模拟启动时的消息发送

**运行方法：**
```bash
python tests/test_telegram_multiple.py
```

### 3. test_startup_notification.py
测试启动推送功能。

**用途：**
- 测试获取币安账户信息
- 测试获取 Hyperliquid 持仓信息
- 测试 Telegram 消息发送

**运行方法：**
```bash
python tests/test_startup_notification.py
```

### 4. test_fills.py
测试 Hyperliquid 订单接口。

**用途：**
- 测试获取用户历史订单
- 验证 API 接口正常
- 测试订单解析功能

**运行方法：**
```bash
python tests/test_fills.py
```

### 5. test_position.py
测试 Hyperliquid 持仓查询。

**用途：**
- 测试获取用户持仓信息
- 验证持仓数据解析
- 显示账户总览

**运行方法：**
```bash
python tests/test_position.py
```

### 6. test_order.py
测试币安开单功能。

**用途：**
- 测试币安 API 连接
- 测试开空单功能
- 验证杠杆设置
- 查询持仓信息

**运行方法：**
```bash
python tests/test_order.py
```

**⚠️ 注意：** 此脚本会实际开单，请在测试网环境下运行！

## 运行所有测试

可以创建一个简单的脚本来运行所有测试：

```bash
#!/bin/bash
echo "运行所有测试..."
echo ""

echo "1. 测试 Telegram 基本功能"
python tests/test_telegram.py
echo ""

echo "2. 测试 Telegram 多消息发送"
python tests/test_telegram_multiple.py
echo ""

echo "3. 测试启动推送功能"
python tests/test_startup_notification.py
echo ""

echo "4. 测试 Hyperliquid 订单接口"
python tests/test_fills.py
echo ""

echo "5. 测试 Hyperliquid 持仓查询"
python tests/test_position.py
echo ""

echo "所有测试完成！"
```

## 测试前准备

1. **配置文件**：确保 `config.py` 已正确配置
2. **API 密钥**：确保币安和 Telegram 的 API 密钥有效
3. **网络连接**：确保能访问币安和 Hyperliquid API
4. **测试环境**：建议先在测试网环境下运行

## 测试日志

测试脚本会生成日志文件：
- `test_telegram_multiple.log` - 多消息测试日志
- `test_startup.log` - 启动推送测试日志
- 其他测试使用主日志文件

## 故障排除

### 问题1：导入错误

**错误信息：** `ModuleNotFoundError: No module named 'xxx'`

**解决方法：**
```bash
pip install -r requirements.txt
```

### 问题2：配置文件未找到

**错误信息：** `ModuleNotFoundError: No module named 'config'`

**解决方法：**
```bash
cp config.example.py config.py
# 然后编辑 config.py 填入实际配置
```

### 问题3：API 连接失败

**可能原因：**
- API 密钥错误
- 网络连接问题
- API 服务器维护

**解决方法：**
- 检查 API 密钥是否正确
- 检查网络连接
- 查看 API 服务状态

## 注意事项

1. **不要在生产环境运行 test_order.py**，它会实际开单
2. 测试脚本可能会产生 API 调用费用
3. 某些测试需要实际的交易数据才能完整测试
4. 建议先在测试网环境下验证所有功能

## 相关文档

- [主 README](../README.md)
- [启动推送说明](../docs/启动推送说明.md)
- [开单状态管理说明](../docs/开单状态管理说明.md)
- [Telegram 通知配置说明](../docs/Telegram通知配置说明.md)

