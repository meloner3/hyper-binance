#!/bin/bash
# 运行所有测试脚本

echo "=================================="
echo "运行所有测试脚本"
echo "=================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 测试计数
TOTAL=0
PASSED=0
FAILED=0

# 运行测试函数
run_test() {
    local test_name=$1
    local test_file=$2
    
    echo "=================================="
    echo "测试: $test_name"
    echo "=================================="
    
    TOTAL=$((TOTAL + 1))
    
    if python "$test_file"; then
        echo -e "${GREEN}✅ $test_name 通过${NC}"
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}❌ $test_name 失败${NC}"
        FAILED=$((FAILED + 1))
    fi
    
    echo ""
    echo "按回车键继续..."
    read
    echo ""
}

# 1. 测试 Telegram 基本功能
run_test "Telegram 基本功能" "tests/test_telegram.py"

# 2. 测试 Telegram 多消息发送
run_test "Telegram 多消息发送" "tests/test_telegram_multiple.py"

# 3. 测试启动推送功能
run_test "启动推送功能" "tests/test_startup_notification.py"

# 4. 测试 Hyperliquid 订单接口
run_test "Hyperliquid 订单接口" "tests/test_fills.py"

# 5. 测试 Hyperliquid 持仓查询
run_test "Hyperliquid 持仓查询" "tests/test_position.py"

# 询问是否测试开单功能
echo "=================================="
echo -e "${YELLOW}⚠️  警告: test_order.py 会实际开单${NC}"
echo "=================================="
echo "是否运行币安开单功能测试? (yes/no)"
read -r response

if [[ "$response" == "yes" ]]; then
    run_test "币安开单功能" "tests/test_order.py"
else
    echo "跳过币安开单功能测试"
    echo ""
fi

# 显示测试结果
echo "=================================="
echo "测试结果汇总"
echo "=================================="
echo "总测试数: $TOTAL"
echo -e "${GREEN}通过: $PASSED${NC}"
echo -e "${RED}失败: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 所有测试通过！${NC}"
    exit 0
else
    echo -e "${RED}⚠️  部分测试失败，请检查日志${NC}"
    exit 1
fi

