"""
测试币安交易功能
测试开10x杠杆，10 USDC的BTC多单
"""
import logging
from logger_config import setup_logger
from binance.client import Client
from binance.enums import *
from binance.exceptions import BinanceAPIException
from config import BINANCE_API_KEY, BINANCE_API_SECRET

# 设置日志
setup_logger(log_file='test_order.log', log_level='INFO')
logger = logging.getLogger(__name__)


def test_open_long_position():
    """测试开多单功能"""
    
    logger.info("=" * 80)
    logger.info("开始测试币安交易功能")
    logger.info("=" * 80)
    
    try:
        # 初始化交易客户端
        logger.info("初始化币安交易客户端...")
        client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)
        client.ping()
        logger.info("✅ 币安客户端初始化成功")
        
        # 测试参数
        symbol = 'BTCUSDC'
        leverage = 10
        margin_usdc = 10  # 保证金10 USDC
        position_value = margin_usdc * leverage  # 持仓价值 = 10 * 10 = 100 USDC
        
        logger.info("")
        logger.info("=" * 80)
        logger.info("测试参数:")
        logger.info(f"  交易对: {symbol}")
        logger.info(f"  杠杆: {leverage}x")
        logger.info(f"  保证金: {margin_usdc} USDC")
        logger.info(f"  持仓价值: {position_value} USDC")
        logger.info(f"  方向: 做多 (LONG)")
        logger.info("=" * 80)
        logger.info("")
        
        # 获取账户余额
        logger.info("📊 查询账户余额...")
        balance = client.futures_account_balance()
        if balance:
            logger.info("当前账户余额:")
            for item in balance:
                if float(item['balance']) > 0:
                    logger.info(f"  {item['asset']}: {item['balance']}")
        logger.info("")
        
        # 1. 设置保证金模式（全仓）
        logger.info("步骤1: 设置保证金模式为全仓...")
        try:
            client.futures_change_margin_type(symbol=symbol, marginType='CROSSED')
            logger.info("✅ 设置为全仓模式")
        except BinanceAPIException as e:
            if 'No need to change margin type' in str(e):
                logger.info("✅ 已经是全仓模式")
            else:
                logger.warning(f"设置保证金模式失败: {e}")
        
        # 2. 设置杠杆
        logger.info(f"步骤2: 设置杠杆为 {leverage}x...")
        response = client.futures_change_leverage(symbol=symbol, leverage=leverage)
        logger.info(f"✅ 杠杆设置成功: {response}")
        
        # 3. 获取当前价格
        logger.info(f"步骤3: 获取当前价格...")
        ticker = client.futures_symbol_ticker(symbol=symbol)
        current_price = float(ticker['price'])
        logger.info(f"  当前价格: {current_price} USDC")
        
        # 4. 计算交易数量
        logger.info(f"步骤4: 计算交易数量...")
        quantity = position_value / current_price
        
        # 获取交易对精度
        exchange_info = client.futures_exchange_info()
        symbol_info = None
        for s in exchange_info['symbols']:
            if s['symbol'] == symbol:
                symbol_info = s
                break
        
        if symbol_info:
            for filter_item in symbol_info['filters']:
                if filter_item['filterType'] == 'LOT_SIZE':
                    step_size = float(filter_item['stepSize'])
                    # 计算精度
                    precision = len(str(step_size).rstrip('0').split('.')[-1])
                    quantity = round(quantity, precision)
                    logger.info(f"  交易精度: {precision} 位小数")
                    logger.info(f"  步长: {step_size}")
                    break
        
        logger.info(f"  计算数量: {quantity} BTC")
        logger.info(f"  预估持仓价值: {quantity * current_price:.2f} USDC")
        
        # 5. 执行开多单
        logger.info(f"步骤5: 执行开多单...")
        logger.info("⚠️  即将执行真实交易！")
        
        order = client.futures_create_order(
            symbol=symbol,
            side=SIDE_BUY,  # 买入做多
            type=ORDER_TYPE_MARKET,
            quantity=quantity,
            positionSide='LONG'  # 指定持仓方向为多头
        )
        
        logger.info("")
        logger.info("=" * 80)
        logger.info("✅ 开多单成功!")
        logger.info("=" * 80)
        logger.info(f"订单信息:")
        logger.info(f"  订单ID: {order.get('orderId')}")
        logger.info(f"  交易对: {order.get('symbol')}")
        logger.info(f"  方向: {order.get('side')}")
        logger.info(f"  类型: {order.get('type')}")
        logger.info(f"  数量: {order.get('origQty')}")
        logger.info(f"  状态: {order.get('status')}")
        if 'avgPrice' in order and order['avgPrice']:
            logger.info(f"  成交均价: {order.get('avgPrice')}")
        logger.info("=" * 80)
        logger.info("")
        
        # 6. 查询持仓信息
        logger.info("📊 查询持仓信息...")
        positions = client.futures_position_information(symbol=symbol)
        if positions:
            for pos in positions:
                position_amt = float(pos.get('positionAmt', 0))
                if position_amt != 0:
                    logger.info("当前持仓:")
                    logger.info(f"  交易对: {pos.get('symbol')}")
                    logger.info(f"  持仓量: {pos.get('positionAmt')}")
                    logger.info(f"  入场价格: {pos.get('entryPrice')}")
                    logger.info(f"  持仓价值: {abs(position_amt) * float(pos.get('entryPrice')):.2f} USDC")
                    logger.info(f"  未实现盈亏: {pos.get('unRealizedProfit')}")
                    logger.info(f"  杠杆: {pos.get('leverage')}x")
                    logger.info(f"  保证金类型: {pos.get('marginType')}")
        
        logger.info("")
        logger.info("=" * 80)
        logger.info("✅ 测试完成!")
        logger.info("=" * 80)
        
        return True
        
    except BinanceAPIException as e:
        logger.error("")
        logger.error("=" * 80)
        logger.error(f"❌ 币安API错误: {e}")
        logger.error("=" * 80)
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
    print("⚠️  警告：这将执行真实的交易操作！")
    print("=" * 80)
    print("测试参数:")
    print("  - 交易对: BTCUSDC")
    print("  - 杠杆: 10x")
    print("  - 保证金: 10 USDC")
    print("  - 持仓价值: 100 USDC")
    print("  - 方向: 做多 (买入)")
    print("=" * 80)
    
    confirm = input("\n确认要执行测试吗？(输入 'yes' 继续): ")
    
    if confirm.lower() == 'yes':
        print("\n开始执行测试...\n")
        success = test_open_long_position()
        
        if success:
            print("\n✅ 测试成功完成！")
        else:
            print("\n❌ 测试失败，请查看日志文件 test_order.log")
    else:
        print("\n已取消测试")
