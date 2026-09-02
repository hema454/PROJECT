from typing import Any

from pydantic import BaseModel, Field


class ExtractionRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Raw text to extract structured data from")
    schema_description: str = Field(..., description="Plain-English description of fields to extract")


class ExtractionResponse(BaseModel):
    request_id: str
    data: dict[str, Any]
    repaired: bool = Field(description="True if json-repair had to fix the model's raw output")


class HealthResponse(BaseModel):
    status: str
    model: str