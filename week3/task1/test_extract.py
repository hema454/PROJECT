from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient


def test_extract_requires_api_key(client: TestClient) -> None:
    resp = client.post("/extract", json={"text": "hi", "schema_description": "name"})
    assert resp.status_code == 401


def test_extract_rejects_wrong_key(client: TestClient) -> None:
    resp = client.post(
        "/extract",
        json={"text": "hi", "schema_description": "name"},
        headers={"x-api-key": "wrong-key"},
    )
    assert resp.status_code == 401


@patch("main.extract", new_callable=AsyncMock)
def test_extract_success(mock_extract, client: TestClient, auth_headers: dict) -> None:
    mock_extract.return_value = ({"name": "Alice"}, False)
    resp = client.post(
        "/extract",
        json={"text": "hi", "schema_description": "name"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["data"] == {"name": "Alice"}
    assert body["repaired"] is False
    assert "request_id" in body
    mock_extract.assert_awaited_once_with("hi", "name")


@patch("main.extract", new_callable=AsyncMock)
def test_extract_repaired_json(mock_extract, client: TestClient, auth_headers: dict) -> None:
    mock_extract.return_value = ({"name": "Bob"}, True)
    resp = client.post(
        "/extract",
        json={"text": "hi", "schema_description": "name"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["repaired"] is True
    assert "request_id" in body


def test_extract_stream_requires_api_key(client: TestClient) -> None:
    resp = client.post("/extract/stream", json={"text": "hi", "schema_description": "name"})
    assert resp.status_code == 401


@patch("main.extract_stream")
def test_extract_stream_success(mock_stream, client: TestClient, auth_headers: dict) -> None:
    async def fake_stream(text, schema_description):
        for tok in ["hello", " world"]:
            yield tok

    mock_stream.side_effect = fake_stream

    resp = client.post(
        "/extract/stream",
        json={"text": "hi", "schema_description": "name"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.text == "hello world"