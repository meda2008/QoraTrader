from pydantic import BaseModel
from typing import Any, Dict, Optional

class IndicatorCalculationRequest(BaseModel):
    indicator_name: str
    data: Any  # The data to calculate the indicator on
    params: Dict[str, Any] = {}  # Additional parameters for the indicator

class IndicatorInfoResponse(BaseModel):
    name: str
    registered: bool
    description: Optional[str] = None