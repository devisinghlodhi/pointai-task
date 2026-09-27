import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app

VALID_B64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="

@pytest.mark.asyncio
async def test_upload_valid_image():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.post("/upload", json={"image": VALID_B64})
    assert res.status_code == 200
    assert res.json() == {"message": "accepted"}

@pytest.mark.asyncio
async def test_upload_invalid_base64():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.post("/upload", json={"image": "not_valid_b64!"})
    assert res.status_code == 422

@pytest.mark.asyncio
async def test_upload_empty_image():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.post("/upload", json={"image": ""})
    assert res.status_code == 422