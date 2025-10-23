// frontend/src/types/risk.ts

export interface RiskParams {
  id: string;
  strategy_id?: string;
  max_position_size: number;
  max_order_size: number;
  max_daily_loss: number;
  max_drawdown: number;
  position_limit_per_symbol: number;
  daily_order_limit: number;
  order_frequency_limit: number;
  risk_level: '低' | '中' | '高';
  is_active: boolean;
  created_at: string;
  updated_at: string;
}