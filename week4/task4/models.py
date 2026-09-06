from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: str  # "user" | "assistant" | "system"
    content: str


class QueryRequest(BaseModel):
    question: str
    conversation_id: str = "default"


class Citation(BaseModel):
    doc_name: str
    page: int
    url: str


class AnswerResponse(BaseModel):
    answer: str
    citations: list[Citation]
    refused: bool