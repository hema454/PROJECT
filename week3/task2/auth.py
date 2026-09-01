import uuid

from fastapi import Header, HTTPException, status

from config import settings


async def get_current_tenant_id(x_api_key: str | None = Header(default=None)) -> uuid.UUID:
    if x_api_key is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="missing API key")
    tenant_id = settings.tenant_map.get(x_api_key)
    if tenant_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid API key")
    return uuid.UUID(tenant_id)