from typing import Callable, Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class EventType(Enum):
    """
    Enum for different types of events in the system
    """
    TICK = "tick"
    BAR = "bar"
    ORDER_UPDATE = "order_update"
    TRADE_UPDATE = "trade_update"
    POSITION_UPDATE = "position_update"
    STRATEGY_SIGNAL = "strategy_signal"
    RISK_ALERT = "risk_alert"
    ACCOUNT_UPDATE = "account_update"
    MARKET_DATA_UPDATE = "market_data_update"

@dataclass
class Event:
    """
    Base event class
    """
    type: EventType
    data: Dict[str, Any]
    timestamp: float
    source: Optional[str] = None

class EventBus:
    """
    A simple event bus for handling events in the trading system
    """
    
    def __init__(self):
        self._handlers: Dict[EventType, List[Callable]] = {}
        self._executor = ThreadPoolExecutor(max_workers=10)
        
    def subscribe(self, event_type: EventType, handler: Callable):
        """
        Subscribe a handler to an event type
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        
        if handler not in self._handlers[event_type]:
            self._handlers[event_type].append(handler)
            logger.info(f"Handler {handler.__name__} subscribed to {event_type.value} events")
    
    def unsubscribe(self, event_type: EventType, handler: Callable):
        """
        Unsubscribe a handler from an event type
        """
        if event_type in self._handlers:
            try:
                self._handlers[event_type].remove(handler)
                logger.info(f"Handler {handler.__name__} unsubscribed from {event_type.value} events")
            except ValueError:
                logger.warning(f"Handler {handler.__name__} was not subscribed to {event_type.value} events")
    
    async def publish(self, event: Event):
        """
        Publish an event to all subscribed handlers
        """
        if event.type in self._handlers:
            tasks = []
            for handler in self._handlers[event.type]:
                try:
                    # Check if handler is async
                    if asyncio.iscoroutinefunction(handler):
                        task = handler(event)
                    else:
                        # Run sync function in thread pool
                        task = asyncio.get_event_loop().run_in_executor(
                            self._executor, 
                            lambda: handler(event)
                        )
                    tasks.append(task)
                except Exception as e:
                    logger.error(f"Error in event handler {handler.__name__}: {str(e)}")
            
            # Execute all tasks concurrently
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
        
        logger.debug(f"Published event {event.type.value} from {event.source or 'unknown source'}")

# Global event bus instance
event_bus = EventBus()

async def publish_event(event_type: EventType, data: Dict[str, Any], source: Optional[str] = None):
    """
    Publish an event using the global event bus
    """
    from time import time
    event = Event(
        type=event_type,
        data=data,
        timestamp=time(),
        source=source
    )
    await event_bus.publish(event)

def subscribe_to_event(event_type: EventType, handler: Callable):
    """
    Subscribe to an event using the global event bus
    """
    event_bus.subscribe(event_type, handler)

def unsubscribe_from_event(event_type: EventType, handler: Callable):
    """
    Unsubscribe from an event using the global event bus
    """
    event_bus.unsubscribe(event_type, handler)