"""
Hyperliquid WebSocket监控模块
使用WebSocket API订阅userFills数据流，避免速率限制问题

根据官方文档: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/websocket/subscriptions
"""
import json
import time
import threading
import logging
from typing import List, Dict, Optional, Callable
from datetime import datetime
import websocket
import requests

logger = logging.getLogger(__name__)


class HyperliquidMonitorWS:
    """Hyperliquid WebSocket交易监控类"""
    
    def __init__(self, api_url: str, ws_url: str, monitor_address: str):
        """
        初始化WebSocket监控器
        
        Args:
            api_url: Hyperliquid HTTP API地址（用于获取持仓等信息）
            ws_url: Hyperliquid WebSocket地址
            monitor_address: 要监控的地址
        """
        self.api_url = api_url
        self.ws_url = ws_url
        self.monitor_address = monitor_address.lower()
        self.processed_fills = set()  # 记录已处理的订单ID
        self.last_position_print_time = 0  # 上次打印持仓的时间
        
        # WebSocket相关
        self.ws = None
        self.ws_connected = False
        self.ws_thread = None
        self.callback = None
        self.running = False
        
        # 统计信息
        self.ws_message_count = 0
        self.ws_error_count = 0
        self.fills_received_count = 0
        
    def _on_ws_message(self, ws, message):
        """WebSocket消息处理"""
        try:
            self.ws_message_count += 1
            data = json.loads(message)
            
            # 检查消息类型
            channel = data.get('channel')
            
            if channel == 'subscriptionResponse':
                # 订阅确认消息
                logger.info(f"✅ WebSocket订阅成功: {data.get('data')}")
                
            elif channel == 'userFills':
                # 用户成交数据
                msg_data = data.get('data', {})
                is_snapshot = msg_data.get('isSnapshot', False)
                fills = msg_data.get('fills', [])
                
                if is_snapshot:
                    logger.info(f"📸 收到历史快照数据: {len(fills)} 条订单")
                    # 快照数据只用于初始化，标记为已处理但不触发回调
                    for fill in fills:
                        fill_id = fill.get('tid', '')
                        if fill_id:
                            self.processed_fills.add(fill_id)
                else:
                    # 实时数据
                    if fills:
                        logger.info(f"📥 收到实时订单数据: {len(fills)} 条")
                        self.fills_received_count += len(fills)
                        close_positions = self.parse_fills(fills)
                        
                        # 触发回调
                        if close_positions and self.callback:
                            for position in close_positions:
                                try:
                                    self.callback(position)
                                except Exception as e:
                                    logger.error(f"执行回调函数时发生错误: {e}")
            
        except json.JSONDecodeError as e:
            logger.error(f"解析WebSocket消息失败: {e}")
            self.ws_error_count += 1
        except Exception as e:
            logger.error(f"处理WebSocket消息时发生错误: {e}")
            self.ws_error_count += 1
    
    def _on_ws_error(self, ws, error):
        """WebSocket错误处理"""
        logger.error(f"❌ WebSocket错误: {error}")
        self.ws_error_count += 1
    
    def _on_ws_close(self, ws, close_status_code, close_msg):
        """WebSocket关闭处理"""
        logger.warning(f"⚠️  WebSocket连接已关闭: {close_status_code} - {close_msg}")
        self.ws_connected = False
        
        # 如果还在运行状态，尝试重连
        if self.running:
            logger.info("尝试重新连接WebSocket...")
            time.sleep(5)
            self._connect_websocket()
    
    def _on_ws_open(self, ws):
        """WebSocket连接建立"""
        logger.info("✅ WebSocket连接已建立")
        self.ws_connected = True
        
        # 发送订阅消息
        subscribe_msg = {
            "method": "subscribe",
            "subscription": {
                "type": "userFills",
                "user": self.monitor_address
            }
        }
        
        logger.info(f"📤 发送订阅请求: {subscribe_msg}")
        ws.send(json.dumps(subscribe_msg))
    
    def _connect_websocket(self):
        """连接WebSocket"""
        try:
            # websocket.enableTrace(True)  # 调试用
            self.ws = websocket.WebSocketApp(
                self.ws_url,
                on_open=self._on_ws_open,
                on_message=self._on_ws_message,
                on_error=self._on_ws_error,
                on_close=self._on_ws_close
            )
            
            # 在新线程中运行WebSocket，启用心跳机制
            # ping_interval: 每30秒发送一次ping
            # ping_timeout: 等待pong响应的超时时间
            self.ws_thread = threading.Thread(
                target=self.ws.run_forever,
                kwargs={
                    'ping_interval': 30,  # 每30秒发送心跳
                    'ping_timeout': 10    # 10秒超时
                }
            )
            self.ws_thread.daemon = True
            self.ws_thread.start()
            
            # 等待连接建立
            timeout = 10
            start_time = time.time()
            while not self.ws_connected and time.time() - start_time < timeout:
                time.sleep(0.1)
            
            if not self.ws_connected:
                logger.error("WebSocket连接超时")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"连接WebSocket失败: {e}")
            return False
    
    def parse_fills(self, fills: List[Dict]) -> List[Dict]:
        """
        解析订单数据，识别平多仓操作
        
        Args:
            fills: 原始订单列表
            
        Returns:
            平多仓操作列表
        """
        close_long_positions = []
        
        if not fills:
            return close_long_positions
        
        try:
            for fill in fills:
                # 获取订单ID，避免重复处理
                fill_id = fill.get('tid', '')
                if fill_id in self.processed_fills:
                    continue
                
                # 获取交易信息
                coin = fill.get('coin', '').upper()
                side = fill.get('side', '')  # 'A' for Ask (卖出), 'B' for Bid (买入)
                closed_pnl = fill.get('closedPnl', '0')
                size = fill.get('sz', '0')
                price = fill.get('px', '0')
                timestamp = fill.get('time', 0)
                
                # 检测是否为平多仓操作
                # 平多仓的特征：
                # 1. side为'A'（卖出）
                # 2. closedPnl不为'0'（有已实现盈亏，说明是平仓）
                # 3. 币种为ETH或BTC
                if (side == 'A' and 
                    closed_pnl != '0' and 
                    coin in ['ETH', 'BTC']):
                    
                    close_long_positions.append({
                        'fill_id': fill_id,
                        'coin': coin,
                        'size': float(size),
                        'price': float(price),
                        'closed_pnl': float(closed_pnl),
                        'timestamp': timestamp,
                        'datetime': datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')
                    })
                    
                    self.processed_fills.add(fill_id)
                    logger.info(f"🎯 检测到平多仓操作: {coin}, 数量: {size}, 价格: {price}, 盈亏: {closed_pnl}")
        
        except Exception as e:
            logger.error(f"解析订单时发生错误: {e}")
        
        return close_long_positions
    
    def get_user_state(self) -> Optional[Dict]:
        """
        获取用户状态（包括持仓信息）
        使用HTTP API
        
        Returns:
            用户状态字典或None（如果请求失败）
        """
        try:
            payload = {
                "type": "clearinghouseState",
                "user": self.monitor_address
            }
            
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data
            else:
                logger.error(f"获取用户状态失败: {response.status_code}, {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"获取用户状态时发生错误: {e}")
            return None
    
    def get_positions_summary(self) -> Optional[Dict]:
        """
        获取持仓信息摘要（用于启动通知）
        
        Returns:
            包含持仓和账户信息的字典
        """
        try:
            user_state = self.get_user_state()
            if not user_state:
                return None
            
            # 获取持仓列表
            positions = user_state.get('assetPositions', [])
            active_positions = []
            
            if positions:
                for pos in positions:
                    position_value = pos.get('position', {})
                    coin = position_value.get('coin', 'UNKNOWN')
                    size = float(position_value.get('szi', 0))
                    
                    # 只记录有持仓的币种
                    if size != 0:
                        entry_px = float(position_value.get('entryPx', 0))
                        unrealized_pnl = float(position_value.get('unrealizedPnl', 0))
                        leverage = position_value.get('leverage', {}).get('value', 0)
                        margin_used = float(position_value.get('marginUsed', 0))
                        liquidation_px = position_value.get('liquidationPx')
                        position_value_usd = abs(size) * entry_px
                        
                        active_positions.append({
                            'coin': coin,
                            'side': '多头' if size > 0 else '空头',
                            'size': size,
                            'entry_price': entry_px,
                            'position_value': position_value_usd,
                            'leverage': leverage,
                            'margin_used': margin_used,
                            'unrealized_pnl': unrealized_pnl,
                            'liquidation_price': float(liquidation_px) if liquidation_px else None
                        })
            
            # 获取账户信息
            margin_summary = user_state.get('marginSummary', {})
            account_value = float(margin_summary.get('accountValue', 0))
            total_margin_used = float(margin_summary.get('totalMarginUsed', 0))
            
            return {
                'positions': active_positions,
                'account_value': account_value,
                'total_margin_used': total_margin_used,
                'available_balance': account_value - total_margin_used
            }
            
        except Exception as e:
            logger.error(f"获取持仓信息摘要失败: {e}")
            return None
    
    def print_positions(self):
        """打印当前持仓状态"""
        try:
            logger.info("=" * 80)
            logger.info(f"📊 查询地址 {self.monitor_address} 的持仓状态")
            logger.info("=" * 80)
            
            user_state = self.get_user_state()
            if not user_state:
                logger.warning("⚠️  无法获取持仓信息")
                return
            
            # 获取持仓列表
            positions = user_state.get('assetPositions', [])
            
            if not positions or len(positions) == 0:
                logger.info("当前无持仓")
                logger.info("=" * 80)
                return
            
            # 显示每个持仓
            has_position = False
            for pos in positions:
                position_value = pos.get('position', {})
                coin = position_value.get('coin', 'UNKNOWN')
                size = float(position_value.get('szi', 0))
                
                # 只显示有持仓的币种
                if size != 0:
                    has_position = True
                    entry_px = float(position_value.get('entryPx', 0))
                    unrealized_pnl = float(position_value.get('unrealizedPnl', 0))
                    leverage = position_value.get('leverage', {}).get('value', 0)
                    margin_used = float(position_value.get('marginUsed', 0))
                    liquidation_px = position_value.get('liquidationPx')
                    
                    position_type = "多头 🟢" if size > 0 else "空头 🔴"
                    position_value_usd = abs(size) * entry_px
                    
                    logger.info(f"\n币种: {coin}")
                    logger.info(f"  方向: {position_type}")
                    logger.info(f"  持仓量: {size}")
                    logger.info(f"  入场价格: ${entry_px:,.2f}")
                    logger.info(f"  持仓价值: ${position_value_usd:,.2f}")
                    logger.info(f"  杠杆: {leverage}x")
                    logger.info(f"  已用保证金: ${margin_used:,.2f}")
                    logger.info(f"  未实现盈亏: ${unrealized_pnl:,.2f}")
                    if liquidation_px:
                        logger.info(f"  强平价格: ${float(liquidation_px):,.2f}")
            
            if not has_position:
                logger.info("当前无持仓")
            
            # 显示账户信息
            margin_summary = user_state.get('marginSummary', {})
            account_value = float(margin_summary.get('accountValue', 0))
            total_margin_used = float(margin_summary.get('totalMarginUsed', 0))
            
            logger.info(f"\n账户总览:")
            logger.info(f"  账户价值: ${account_value:,.2f}")
            logger.info(f"  已用保证金: ${total_margin_used:,.2f}")
            logger.info(f"  可用余额: ${account_value - total_margin_used:,.2f}")
            
            logger.info("=" * 80)
            
        except Exception as e:
            logger.error(f"打印持仓信息时发生错误: {e}", exc_info=True)
    
    def print_latest_fill(self) -> bool:
        """
        打印最近一笔订单记录，用于验证API接口正常
        使用HTTP API
        """
        try:
            logger.info("=" * 80)
            logger.info("🔍 测试API接口 - 获取最近一笔订单记录")
            logger.info("=" * 80)
            
            payload = {
                "type": "userFills",
                "user": self.monitor_address
            }
            
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=10
            )
            
            if response.status_code != 200:
                logger.error("❌ 无法获取订单数据，API接口可能异常")
                return False
            
            fills = response.json()
            
            if not fills or len(fills) == 0:
                logger.warning("⚠️  该地址暂无订单记录")
                logger.info("=" * 80)
                return True
            
            # 获取最新的一笔订单
            latest_fill = fills[0]
            
            coin = latest_fill.get('coin', 'UNKNOWN')
            side = latest_fill.get('side', '')
            side_text = '卖出' if side == 'A' else '买入'
            size = latest_fill.get('sz', '0')
            price = latest_fill.get('px', '0')
            closed_pnl = latest_fill.get('closedPnl', '0')
            timestamp = latest_fill.get('time', 0)
            datetime_str = datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')
            
            logger.info("✅ API接口正常！")
            logger.info(f"\n最近一笔订单:")
            logger.info(f"  时间: {datetime_str}")
            logger.info(f"  币种: {coin}")
            logger.info(f"  方向: {side_text}")
            logger.info(f"  数量: {size}")
            logger.info(f"  价格: {price}")
            logger.info(f"  已实现盈亏: {closed_pnl}")
            logger.info(f"\n总订单数: {len(fills)} 条")
            logger.info("=" * 80)
            
            return True
            
        except Exception as e:
            logger.error(f"打印最近订单时发生错误: {e}", exc_info=True)
            return False
    
    def start_monitoring(self, callback: Callable, position_print_interval: int = 300):
        """
        开始WebSocket监控
        
        Args:
            callback: 检测到平仓时的回调函数
            position_print_interval: 打印持仓间隔（秒），默认300秒（5分钟）
        """
        logger.info(f"🚀 开始WebSocket监控地址: {self.monitor_address}")
        logger.info(f"持仓状态打印间隔: {position_print_interval}秒 ({position_print_interval//60}分钟)")
        logger.info("")
        
        self.callback = callback
        self.running = True
        
        # 1. 测试API接口 - 打印最近一笔订单
        if not self.print_latest_fill():
            logger.error("⚠️  API接口测试失败，但程序将继续运行")
        logger.info("")
        
        # 2. 打印当前持仓状态
        self.print_positions()
        self.last_position_print_time = time.time()
        logger.info("")
        
        # 3. 连接WebSocket
        logger.info("正在连接WebSocket...")
        if not self._connect_websocket():
            logger.error("❌ WebSocket连接失败")
            return
        
        logger.info("✅ WebSocket监控已启动")
        logger.info("📡 等待实时订单数据...")
        logger.info("")
        
        # 4. 主循环 - 定期打印持仓和统计信息
        try:
            while self.running:
                time.sleep(10)  # 每10秒检查一次
                
                current_time = time.time()
                
                # 检查是否需要打印持仓
                if current_time - self.last_position_print_time >= position_print_interval:
                    self.print_positions()
                    self.last_position_print_time = current_time
                    
                    # 打印统计信息
                    logger.info(f"📊 WebSocket统计: 总消息={self.ws_message_count}, "
                              f"收到订单={self.fills_received_count}, "
                              f"错误={self.ws_error_count}")
                
        except KeyboardInterrupt:
            logger.info("监控已停止")
        finally:
            self.stop()
    
    def stop(self):
        """停止监控"""
        logger.info("正在停止WebSocket监控...")
        self.running = False
        
        if self.ws:
            self.ws.close()
        
        logger.info("✅ WebSocket监控已停止")

