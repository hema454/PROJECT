from datetime import date
from typing import Dict

from pydantic import BaseModel, Field


class ExchangeRateResponse(BaseModel):

    result: str
    base_code: str
    time_last_update_utc: str
    time_next_update_utc: str
    rates: Dict[str, float]


class ConversionResult(BaseModel):

    base_currency: str
    target_currency: str
    rate: float
    amount: float
    converted_amount: float = Field(..., description="amount * rate")
    last_updated_utc: str