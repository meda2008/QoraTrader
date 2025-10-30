import asyncio
from typing import Dict, List, Callable, Any
from dataclasses import dataclass
from enum import Enum

class EventType(Enum):
    ORDER_SUBMITTED = "order_submitted"
    ORDER_FILLED = "order_filled"
    ORDER_CANCELLED = "order_cancelled"
    POSITION_CHANGED = "position_changed"
    PRICE_UPDATED = "price_updated"
    STRATEGY_SIGNAL = "strategy_signal"
    RISK_ALERT = "risk_alert"

@dataclass
class Event:
    type: EventType
    data: Dict[str, Any]
    timestamp: float = None

class EventBus:
    def __init__(self):
        self._subscribers: Dict[EventType, List[Callable]] = {}
        self._loop = asyncio.get_event_loop()

    def subscribe(self, event_type: EventType, handler: Callable):
        """订阅事件"""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)

    def unsubscribe(self, event_type: EventType, handler: Callable):
        """取消订阅事件"""
        if event_type in self._subscribers:
            try:
                self._subscribers[event_type].remove(handler)
            except ValueError:
                pass  # Handler not found

    async def publish(self, event: Event):
        """发布事件"""
        if event.type in self._subscribers:
            for handler in self._subscribers[event.type]:
                # 异步执行处理函数，避免阻塞事件发布
                asyncio.create_task(handler(event))

    def emit_sync(self, event_type: EventType, data: Dict[str, Any]):
        """同步发布事件"""
        event = Event(type=event_type, data=data)
        if event_type in self._subscribers:
            for handler in self._subscribers[event_type]:
                # 在事件循环中运行同步处理函数
                asyncio.run_coroutine_threadsafe(handler(event), self._loop)

# 全局事件总线实例
event_bus = EventBus()