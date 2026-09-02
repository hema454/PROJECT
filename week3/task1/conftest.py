import pytest
from fastapi.testclient import TestClient

from config import settings
from main import app


@pytest.fixture
def api_key() -> str:
    return settings.api_key


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def auth_headers(api_key: str) -> dict[str, str]:
    return {"x-api-key": api_key}