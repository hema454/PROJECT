import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ExtractionRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Raw text to extract structured data from")
    schema_description: str = Field(..., description="Plain-English description of fields to extract")
    conversation_id: uuid.UUID | None = Field(
        default=None, description="Reuse an existing conversation; omit to start a new one"
    )


class ExtractionResponse(BaseModel):
    request_id: str
    conversation_id: uuid.UUID
    data: dict[str, Any]
    repaired: bool = Field(description="True if json-repair had to fix the model's raw output")


class HealthResponse(BaseModel):
    status: str
    model: str


class MessageResponse(BaseModel):
    message_id: uuid.UUID
    role: str
    content: str
    created_at: datetime


class ConversationResponse(BaseModel):
    conversation_id: uuid.UUID
    conversation_created_at: datetime
    messages: list[MessageResponse]