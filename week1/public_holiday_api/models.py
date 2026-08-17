from typing import Optional
from pydantic import BaseModel, Field


class PublicHoliday(BaseModel):
    date: str
    localName: str
    name: str
    countryCode: str
    fixed: bool
    global_: bool = Field(True, alias="global")  # 'global' is a Python keyword
    counties: Optional[list[str]] = None
    types: Optional[list[str]] = None

    model_config = {"populate_by_name": True}


class CountryInfo(BaseModel):
    countryCode: str
    name: str