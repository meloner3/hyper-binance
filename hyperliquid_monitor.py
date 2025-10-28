"""
Hyperliquid API监控模块
用于监控指定地址的交易订单

注意：Hyperliquid官方未公布具体的API速率限制
建议保守使用，避免过于频繁的请求
推荐频率：公开数据接口每秒不超过2-5次
"""
import requests
import time
from typing import List, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# API速率限制配置（保守估计）
API_REQUEST_DELAY = 0.2  # 每次请求之间至少间隔0.2秒（即每秒最多5次）


class HyperliquidMonitor:
    """Hyperliquid交易监控类"""
    
    def __init__(self, api_url: str, monitor_address: str, user_fills_limit: int = 20):
        """
        初始化监控器
        
        Args:
            api_url: Hyperliquid API地址
            monitor_address: 要监控的地址
            user_fills_limit: 每次获取的订单数量，默认20条
        """
        self.api_url = api_url
        self.monitor_address = monitor_address.lower()
        self.user_fills_limit = user_fills_limit
        self.last_processed_time = 0
        self.processed_fills = set()  # 记录已处理的订单ID
        self.last_position_print_time = 0  # 上次打印持仓的时间
        self.last_api_request_time = 0  # 上次API请求的时间
        self.api_request_count = 0  # API请求计数
        self.api_error_count = 0  # API错误计数
        
    def _rate_limit_check(self):
        """检查并执行速率限制"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_api_request_time
        
        if time_since_last_request < API_REQUEST_DELAY:
            sleep_time = API_REQUEST_DELAY - time_since_last_request
            logger.debug(f"速率限制：等待 {sleep_time:.2f} 秒")
            time.sleep(sleep_time)
        
        self.last_api_request_time = time.time()
        self.api_request_count += 1
    
    def get_user_fills(self, limit: int = 20) -> Optional[List[Dict]]:
        """
        获取用户的历史订单
        
        Args:
            limit: 返回的最大订单数量，默认20条
        
        Returns:
            订单列表或None（如果请求失败）
        """
        try:
            # 速率限制检查
            self._rate_limit_check()
            
            payload = {
                "type": "userFills",
                "user": self.monitor_address
            }
            
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                total_count = len(data) if data else 0
                
                # 只返回最近的N条数据
                if data and len(data) > limit:
                    data = data[:limit]
                    logger.debug(f"成功获取订单数据: {total_count}条，返回最近{limit}条")
                else:
                    logger.debug(f"成功获取订单数据: {total_count}条")
                
                return data
            elif response.status_code == 429:
                # 速率限制错误
                self.api_error_count += 1
                logger.warning(f"⚠️ API速率限制！已触发 {self.api_error_count} 次")
                time.sleep(5)  # 等待5秒后重试
                return None
            else:
                logger.error(f"API请求失败: {response.status_code}, {response.text}")
                self.api_error_count += 1
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"请求异常: {e}")
            self.api_error_count += 1
            return None
        except Exception as e:
            logger.error(f"获取订单时发生错误: {e}")
            self.api_error_count += 1
            return None
    
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
                    logger.info(f"检测到平多仓操作: {coin}, 数量: {size}, 价格: {price}, 盈亏: {closed_pnl}")
        
        except Exception as e:
            logger.error(f"解析订单时发生错误: {e}")
        
        return close_long_positions
    
    def get_user_state(self) -> Optional[Dict]:
        """
        获取用户状态（包括持仓信息）
        
        Returns:
            用户状态字典或None（如果请求失败）
        """
        try:
            # 速率限制检查
            self._rate_limit_check()
            
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
            elif response.status_code == 429:
                # 速率限制错误
                self.api_error_count += 1
                logger.warning(f"⚠️ API速率限制！已触发 {self.api_error_count} 次")
                time.sleep(5)  # 等待5秒后重试
                return None
            else:
                logger.error(f"获取用户状态失败: {response.status_code}, {response.text}")
                self.api_error_count += 1
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"请求异常: {e}")
            self.api_error_count += 1
            return None
        except Exception as e:
            logger.error(f"获取用户状态时发生错误: {e}")
            self.api_error_count += 1
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
            total_unrealized_pnl = float(margin_summary.get('totalNtlPos', 0))
            
            logger.info(f"\n账户总览:")
            logger.info(f"  账户价值: ${account_value:,.2f}")
            logger.info(f"  已用保证金: ${total_margin_used:,.2f}")
            logger.info(f"  可用余额: ${account_value - total_margin_used:,.2f}")
            
            logger.info("=" * 80)
            
        except Exception as e:
            logger.error(f"打印持仓信息时发生错误: {e}", exc_info=True)
    
    def print_latest_fill(self):
        """打印最近一笔订单记录，用于验证API接口正常"""
        try:
            logger.info("=" * 80)
            logger.info("🔍 测试API接口 - 获取最近一笔订单记录")
            logger.info("=" * 80)
            
            fills = self.get_user_fills(limit=self.user_fills_limit)
            
            if fills is None:
                logger.error("❌ 无法获取订单数据，API接口可能异常")
                return False
            
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
    
    def scan_once(self) -> List[Dict]:
        """
        执行一次扫描
        
        Returns:
            检测到的平多仓操作列表
        """
        logger.debug(f"开始扫描地址: {self.monitor_address}")
        
        fills = self.get_user_fills(limit=self.user_fills_limit)
        if fills is None:
            return []
        
        close_positions = self.parse_fills(fills)
        
        if close_positions:
            logger.info(f"本次扫描发现 {len(close_positions)} 个平多仓操作")
        
        return close_positions
    
    def start_monitoring(self, scan_interval: int, callback, position_print_interval: int = 300):
        """
        开始持续监控
        
        Args:
            scan_interval: 扫描间隔（秒）
            callback: 检测到平仓时的回调函数
            position_print_interval: 打印持仓间隔（秒），默认300秒（5分钟）
        """
        logger.info(f"开始监控地址: {self.monitor_address}, 扫描间隔: {scan_interval}秒")
        logger.info(f"持仓状态打印间隔: {position_print_interval}秒 ({position_print_interval//60}分钟)")
        logger.info("")
        
        # 1. 测试API接口 - 打印最近一笔订单
        if not self.print_latest_fill():
            logger.error("⚠️  API接口测试失败，但程序将继续运行")
        logger.info("")
        
        # 2. 打印当前持仓状态
        self.print_positions()
        self.last_position_print_time = time.time()
        logger.info("")
        
        while True:
            try:
                current_time = time.time()
                
                # 检查是否需要打印持仓
                if current_time - self.last_position_print_time >= position_print_interval:
                    self.print_positions()
                    self.last_position_print_time = current_time
                
                # 扫描订单
                close_positions = self.scan_once()
                
                # 如果检测到平仓操作，调用回调函数
                for position in close_positions:
                    try:
                        callback(position)
                    except Exception as e:
                        logger.error(f"执行回调函数时发生错误: {e}")
                
                time.sleep(scan_interval)
                
            except KeyboardInterrupt:
                logger.info("监控已停止")
                break
            except Exception as e:
                logger.error(f"监控循环发生错误: {e}")
                time.sleep(scan_interval)

