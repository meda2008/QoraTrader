import { message } from 'antd';

class WebSocketService {
  private ws: WebSocket | null = null;
  private url: string;
  private reconnectInterval: number = 5000;
  private reconnectAttempts: number = 0;
  private maxReconnectAttempts: number = 5;
  private eventHandlers: { [key: string]: Array<(data: any) => void> } = {};

  constructor(url: string) {
    this.url = url;
  }

  connect() {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      return;
    }

    this.ws = new WebSocket(this.url);

    this.ws.onopen = (event) => {
      console.log('WebSocket connected:', event);
      this.reconnectAttempts = 0; // 重置重连计数
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        const { type, payload } = data;

        if (this.eventHandlers[type]) {
          this.eventHandlers[type].forEach(handler => handler(payload));
        }
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    this.ws.onclose = (event) => {
      console.log('WebSocket disconnected:', event);
      
      if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
        // 自动重连
        setTimeout(() => {
          this.reconnectAttempts++;
          this.connect();
        }, this.reconnectInterval);
      } else {
        message.error(`WebSocket连接已断开，错误代码: ${event.code}`);
      }
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }

  disconnect() {
    if (this.ws) {
      this.ws.close(1000, 'Manually disconnected');
      this.ws = null;
    }
  }

  send(type: string, data: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type, payload: data }));
    } else {
      console.error('WebSocket is not connected');
    }
  }

  subscribe(eventType: string, handler: (data: any) => void) {
    if (!this.eventHandlers[eventType]) {
      this.eventHandlers[eventType] = [];
    }
    this.eventHandlers[eventType].push(handler);
  }

  unsubscribe(eventType: string, handler: (data: any) => void) {
    if (this.eventHandlers[eventType]) {
      this.eventHandlers[eventType] = this.eventHandlers[eventType].filter(h => h !== handler);
    }
  }

  isConnected() {
    return this.ws && this.ws.readyState === WebSocket.OPEN;
  }
}

// 创建全局WebSocket实例
const wsUrl = process.env.REACT_APP_WS_URL || `ws://${window.location.host}/api/v1/ws`;
const websocketService = new WebSocketService(wsUrl);

export default websocketService;