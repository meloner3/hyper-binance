#!/bin/bash
# WebSocket 修复测试脚本

echo "=========================================="
echo "WebSocket 连接稳定性测试"
echo "=========================================="
echo ""
echo "此脚本将运行5分钟的稳定性测试"
echo "测试内容："
echo "  1. 监控连接是否稳定"
echo "  2. 检查心跳机制是否正常"
echo "  3. 统计重连次数"
echo ""
echo "按 Ctrl+C 可以随时停止测试"
echo ""
read -p "按回车键开始测试..." 

python tests/test_websocket_stability.py

echo ""
echo "=========================================="
echo "测试完成！"
echo "=========================================="
echo ""
echo "请查看日志文件了解详细信息："
echo "  - test_websocket_stability.log"
echo ""

