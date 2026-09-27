import base64
import os
import socket
from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel, field_validator

NODE_ID = os.getenv("HOSTNAME", socket.gethostname())

app = FastAPI(title="Image Processing Service")


class ImageRequest(BaseModel):
    image: str

    @field_validator("image")
    @classmethod
    def check_base64(cls, val: str) -> str:
        raw_b64 = val.split(",", 1)[-1] if "," in val else val
        try:
            decoded = base64.b64decode(raw_b64, validate=True)
            if not decoded:
                raise ValueError("Payload contains empty data")
        except Exception:
            raise ValueError("Payload must be a valid base64 encoded image")
        return raw_b64


@app.get("/healthz", status_code=status.HTTP_200_OK)
async def health():
    return {"status": "ok", "worker_node": NODE_ID}


@app.post("/upload", status_code=status.HTTP_200_OK)
async def process_image(payload: ImageRequest, response: Response):
    # Track which container processed this request
    response.headers["X-Worker-Node"] = NODE_ID
    return {"message": "accepted"}