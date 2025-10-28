"""
开单状态管理脚本
用于查看和重置开单状态
"""
import json
import os
import sys
from datetime import datetime

TRADE_STATE_FILE = 'trade_state.json'


def load_trade_state():
    """加载开单状态"""
    if os.path.exists(TRADE_STATE_FILE):
        with open(TRADE_STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_trade_state(state):
    """保存开单状态"""
    with open(TRADE_STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def display_state(state):
    """显示当前状态"""
    print("\n" + "=" * 60)
    print("当前开单状态")
    print("=" * 60)
    
    if not state:
        print("当前无开单记录")
    else:
        for coin, info in state.items():
            if info.get('opened', False):
                print(f"\n币种: {coin}")
                print(f"  状态: 已开单")
                print(f"  时间: {info.get('timestamp', 'N/A')}")
                print(f"  订单ID: {info.get('order_id', 'N/A')}")
    
    print("=" * 60 + "\n")


def reset_coin(state, coin):
    """重置指定币种的状态"""
    if coin in state:
        del state[coin]
        print(f"✅ 已重置 {coin} 的开单状态")
        return True
    else:
        print(f"⚠️  {coin} 没有开单记录")
        return False


def reset_all(state):
    """重置所有币种的状态"""
    state.clear()
    print("✅ 已重置所有币种的开单状态")


def main():
    """主函数"""
    print("\n🤖 开单状态管理工具")
    
    # 加载当前状态
    state = load_trade_state()
    
    while True:
        display_state(state)
        
        print("请选择操作:")
        print("1. 重置指定币种的开单状态")
        print("2. 重置所有币种的开单状态")
        print("3. 刷新显示")
        print("4. 退出")
        
        choice = input("\n请输入选项 (1-4): ").strip()
        
        if choice == '1':
            coin = input("请输入币种名称 (如 ETH, BTC): ").strip().upper()
            if reset_coin(state, coin):
                save_trade_state(state)
                print("状态已保存到文件")
        
        elif choice == '2':
            confirm = input("确认要重置所有币种的状态吗? (yes/no): ").strip().lower()
            if confirm == 'yes':
                reset_all(state)
                save_trade_state(state)
                print("状态已保存到文件")
            else:
                print("已取消操作")
        
        elif choice == '3':
            state = load_trade_state()
            print("已刷新状态")
        
        elif choice == '4':
            print("退出程序")
            break
        
        else:
            print("⚠️  无效的选项，请重新选择")
        
        input("\n按回车键继续...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序已中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        sys.exit(1)

