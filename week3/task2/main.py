import json
import logging
import uuid

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

import service
from auth import get_current_tenant_id
from config import settings
from db import get_db
from logging_setup import configure_logging, request_id_var
from models import (
    ConversationResponse,
    ExtractionRequest,
    ExtractionResponse,
    HealthResponse,
    MessageResponse,
)

configure_logging(settings.log_level)
logger = logging.getLogger(__name__)

logger.info(
    "startup config: model=%s temperature=%s timeout=%s base_url=%s",
    settings.ollama_model, settings.temperature, settings.timeout_seconds, settings.ollama_base_url,
)

app = FastAPI(title="Extraction Service", version="1.0.0")


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    token = request_id_var.set(request_id)
    try:
        logger.info("%s %s", request.method, request.url.path)
        response = await call_next(request)
    finally:
        request_id_var.reset(token)
    response.headers["X-Request-ID"] = request_id
    return response


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok", model=settings.ollama_model)


@app.post("/extract", response_model=ExtractionResponse)
async def extract_endpoint(
    req: ExtractionRequest,
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
) -> ExtractionResponse:
    request_id = request_id_var.get()

    conversation = await service.get_or_create_conversation(db, tenant_id, req.conversation_id)
    conversation_id = conversation.id

    history = await service.get_conversation_history(db, tenant_id, conversation_id)
    await db.rollback()

    try:
        data, repaired = await service.extract(req.text, req.schema_description, history)
    except service.ExtractionError as exc:
        raise HTTPException(status_code=502, detail="model call failed") from exc

    await service.record_exchange(
        db, tenant_id, conversation_id, user_text=req.text, assistant_content=json.dumps(data)
    )

    return ExtractionResponse(
        request_id=request_id, conversation_id=conversation_id, data=data, repaired=repaired
    )


@app.post("/extract/stream")
async def extract_stream_endpoint(
    req: ExtractionRequest,
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
) -> StreamingResponse:
    conversation = await service.get_or_create_conversation(db, tenant_id, req.conversation_id)
    conversation_id = conversation.id

    history = await service.get_conversation_history(db, tenant_id, conversation_id)
    await db.rollback()

    async def token_gen():
        chunks: list[str] = []
        try:
            async for token in service.extract_stream(req.text, req.schema_description, history):
                chunks.append(token)
                yield token
        except service.ExtractionError:
            yield "\n[error: model call failed]\n"
            return

        await service.record_exchange(
            db, tenant_id, conversation_id, user_text=req.text, assistant_content="".join(chunks)
        )

    return StreamingResponse(
        token_gen(), media_type="text/plain", headers={"X-Conversation-Id": str(conversation_id)}
    )


@app.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def replay_conversation(
    conversation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
) -> ConversationResponse:
    try:
        conversation, messages = await service.replay_conversation(db, tenant_id, conversation_id)
    except service.ConversationNotFoundError:
        raise HTTPException(status_code=404, detail="conversation not found")

    return ConversationResponse(
        conversation_id=conversation_id,
        conversation_created_at=conversation.created_at,
        messages=[
            MessageResponse(message_id=m.id, role=m.role, content=m.content, created_at=m.created_at)
            for m in messages
        ],
    )