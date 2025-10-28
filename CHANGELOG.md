# 更新日志

所有重要的项目更改都将记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
并且本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [1.3.1] - 2025-10-28

### 修复
- 🐛 **WebSocket连接稳定性问题**（重要修复）
  - 修复连接每60秒因"Inactive"断开的问题
  - 实现应用层保活机制：每30秒发送JSON格式的ping消息
  - 添加连接健康检测：超过50秒无消息自动重连
  - 禁用websocket-client的自动ping，改用应用层保活
  - 实现指数退避重连策略（5秒 → 7.5秒 → 11.25秒 → 最多30秒）
  - 新增心跳统计信息（ping/pong次数、重连次数）
  - 连接成功后自动重置重连计数器

### 新增
- 🧪 **WebSocket稳定性测试**
  - 新增 `tests/test_websocket_stability.py` - 5分钟稳定性测试
  - 新增 `test_ws_fix.sh` - 快速运行测试脚本
  - 新增 `WEBSOCKET_FIX.md` - 详细的修复说明文档

### 改进
- 📊 **统计信息增强**
  - 添加ping/pong计数到定期报告
  - 添加重连次数统计
  - 添加上次pong时间监控
  - DEBUG级别日志显示详细心跳信息

## [1.3.0] - 2025-10-28

### 新增
- 🚀 **WebSocket实时推送功能**（重要更新）
  - 新增 `hyperliquid_monitor_ws.py` WebSocket监控模块
  - 使用 Hyperliquid WebSocket API 订阅 `userFills` 数据流
  - 实时接收订单成交推送，无延迟，无速率限制
  - 自动重连机制，确保连接稳定性
  - 支持快照数据初始化，避免重复处理历史订单
  - **心跳机制**：每30秒自动发送ping，保持连接活跃（解决60秒超时断开问题）

- ⚙️ **监控模式配置**
  - 新增 `USE_WEBSOCKET` 配置项，可选择 WebSocket 或 HTTP 轮询模式
  - WebSocket 模式为默认推荐模式
  - 保留 HTTP 轮询模式作为备选方案

- 🧪 **WebSocket 测试脚本**
  - 新增 `tests/test_websocket.py` 用于测试 WebSocket 连接

### 改进
- 📡 **避免速率限制问题**
  - WebSocket 模式无需轮询，完全避免 API 速率限制
  - 实时推送比轮询更及时，响应更快

- 📊 **统计信息增强**
  - WebSocket 模式新增消息统计、订单接收统计、错误统计

### 依赖
- ➕ 新增 `websocket-client==1.6.4` 依赖

### 文档
- 📝 更新 README.md，说明 WebSocket 功能
- 📝 更新配置示例，添加 WebSocket 相关配置

## [1.2.0] - 2025-10-28

### 新增
- ✨ **开单状态管理功能**
  - 自动记录每个币种的开单状态
  - 防止重复开单
  - 状态持久化保存到文件
  - 提供交互式管理工具 `reset_trade_state.py`
  - 跳过重复开单时发送 Telegram 通知

- ✨ **项目结构优化**
  - 创建 `tests/` 目录统一管理测试脚本
  - 创建 `docs/` 目录统一管理文档
  - 添加各目录的 README 说明文件

### 修复
- 🐛 **Telegram 事件循环错误**
  - 修复 "Event loop is closed" 错误
  - 改为重用事件循环，避免频繁创建和销毁
  - 提升连续发送多条消息的稳定性

### 文档
- 📝 添加 `开单状态管理说明.md`
- 📝 添加 `Telegram事件循环修复说明.md`
- 📝 更新主 README，添加新功能说明
- 📝 创建 `tests/README.md` 测试说明
- 📝 创建 `docs/README.md` 文档索引
- 📝 创建 `CHANGELOG.md` 更新日志

### 变更
- 📦 重组项目结构，测试脚本移至 `tests/` 目录
- 📦 文档文件移至 `docs/` 目录
- 🔧 更新 `.gitignore`，添加 `trade_state.json`

## [1.1.0] - 2025-10-28

### 新增
- ✨ **启动推送功能**
  - 程序启动时自动推送系统启动通知
  - 自动推送币安合约账户余额和持仓信息
  - 自动推送监控地址的持仓信息
  - 所有信息通过 Telegram 发送

- ✨ **账户信息获取**
  - 新增 `BinanceTrader.get_account_info_summary()` 方法
  - 新增 `HyperliquidMonitor.get_positions_summary()` 方法
  - 新增 `TelegramNotifier.send_binance_account_info()` 方法
  - 新增 `TelegramNotifier.send_hyperliquid_positions()` 方法

### 文档
- 📝 添加 `启动推送说明.md`
- 📝 添加 `更新日志_启动推送.md`
- 📝 添加 `test_startup_notification.py` 测试脚本

## [1.0.0] - 2025-10-28

### 新增
- ✨ **核心功能**
  - 实时监控 Hyperliquid 指定地址的交易订单
  - 自动检测 ETH 和 BTC 的平多仓操作
  - 自动在币安交易所开空单
  - 完整的日志记录和错误处理
  - 可配置的杠杆倍数和持仓量

- ✨ **Telegram 通知功能**
  - 系统启动通知
  - 平仓检测警报
  - 交易成功/失败通知
  - API 测试结果通知
  - 错误警报

- ✨ **持仓监控功能**
  - 定时打印 Hyperliquid 持仓状态
  - 显示账户总览信息
  - 显示每个持仓的详细信息

### 模块
- 📦 `main.py` - 主程序入口
- 📦 `binance_trader.py` - 币安交易模块
- 📦 `hyperliquid_monitor.py` - Hyperliquid 监控模块
- 📦 `telegram_notifier.py` - Telegram 通知模块
- 📦 `logger_config.py` - 日志配置模块

### 配置
- ⚙️ `config.example.py` - 配置文件模板
- ⚙️ 支持测试网和正式网切换
- ⚙️ 可配置的扫描间隔和持仓打印间隔

### 测试
- 🧪 `test_telegram.py` - Telegram 通知测试
- 🧪 `test_fills.py` - Hyperliquid 订单接口测试
- 🧪 `test_position.py` - Hyperliquid 持仓查询测试
- 🧪 `test_order.py` - 币安开单功能测试

### 文档
- 📝 `README.md` - 项目说明
- 📝 `Telegram通知配置说明.md` - Telegram 配置说明
- 📝 `API速率限制说明.md` - API 速率限制说明
- 📝 `持仓监控说明.md` - 持仓监控功能说明
- 📝 `启动检查说明.md` - 启动检查流程说明

## 版本说明

### 版本号规则
- **主版本号**：重大功能变更或不兼容的 API 修改
- **次版本号**：向下兼容的功能性新增
- **修订号**：向下兼容的问题修正

### 标签说明
- ✨ 新增功能
- 🐛 Bug 修复
- 📝 文档更新
- 🔧 配置修改
- 📦 模块/文件变更
- ⚙️ 配置项变更
- 🧪 测试相关
- 🎨 代码格式/结构优化
- ⚡️ 性能优化
- 🔒 安全相关

## 计划功能

### v1.3.0（计划中）
- [ ] 添加 Web 管理界面
- [ ] 支持更多交易对
- [ ] 添加止盈止损功能
- [ ] 添加交易统计和分析
- [ ] 支持多地址监控

### v1.4.0（计划中）
- [ ] 添加策略配置功能
- [ ] 支持自定义交易规则
- [ ] 添加回测功能
- [ ] 支持更多交易所

## 贡献指南

如果你想为项目做贡献：

1. Fork 本仓库
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的修改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启一个 Pull Request

## 问题反馈

如果你发现了 Bug 或有功能建议：

1. 查看 [Issues](https://github.com/yourusername/hypegendan/issues) 是否已有相关问题
2. 如果没有，创建一个新的 Issue
3. 详细描述问题或建议
4. 如果是 Bug，请提供复现步骤和日志

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

---

**注意**：本项目仅供学习和研究使用。使用本程序进行实际交易的所有风险由使用者自行承担。

