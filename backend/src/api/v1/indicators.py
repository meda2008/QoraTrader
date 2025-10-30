from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
import pandas as pd
from ..database import get_db
from ..indicators.service import IndicatorService

router = APIRouter()
indicator_service = IndicatorService()

@router.get("/available")
def get_available_indicators():
    """获取可用的指标列表"""
    return {"indicators": indicator_service.get_available_indicators()}

@router.post("/calculate/{indicator_name}")
def calculate_indicator(
    indicator_name: str, 
    data: Dict[str, Any], 
    params: Dict[str, Any] = None,
    db: Session = Depends(get_db)
):
    """计算技术指标"""
    try:
        # 将数据转换为pandas Series
        if 'values' in data:
            series_data = pd.Series(data['values'])
        elif 'close' in data:
            # 如果提供的是OHLCV数据，则使用收盘价
            series_data = pd.Series(data['close'])
        else:
            raise HTTPException(status_code=400, detail="Invalid data format")
        
        # 设置默认参数
        if params is None:
            params = {}
        
        # 计算指标
        result = indicator_service.calculate(indicator_name, series_data, **params)
        
        # 将结果转换为可序列化的格式
        if isinstance(result, pd.Series):
            return {"result": result.tolist()}
        elif isinstance(result, dict):
            serializable_result = {}
            for key, value in result.items():
                if isinstance(value, pd.Series):
                    serializable_result[key] = value.tolist()
                else:
                    serializable_result[key] = value
            return {"result": serializable_result}
        else:
            return {"result": result}
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")