import logging
import uuid

from fastapi import Depends, FastAPI, Request
from fastapi.responses import StreamingResponse

from auth import verify_api_key
from config import settings
from logging_setup import configure_logging, request_id_var
from models import ExtractionRequest, ExtractionResponse, HealthResponse
from service import extract, extract_stream, ExtractionError

configure_logging(settings.log_level)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Extraction Service",
    version="1.0.0",
    dependencies=[Depends(verify_api_key)],
)


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
async def extract_endpoint(req: ExtractionRequest) -> ExtractionResponse:
    data, repaired = await extract(req.text, req.schema_description)
    return ExtractionResponse(
        data=data,
        repaired=repaired,
        request_id=request_id_var.get(),
    )

@app.post("/extract/stream")
async def extract_stream_endpoint(req: ExtractionRequest) -> StreamingResponse:
    return StreamingResponse(
        extract_stream(req.text, req.schema_description),
        media_type="text/plain",
    )