import os
from typing import Any

import httpx
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, Response

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8081")
SEMANTIC_SERVICE_URL = os.getenv("SEMANTIC_SERVICE_URL", "http://localhost:9000")

router = APIRouter()


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "backend": BACKEND_URL, "semantic_service": SEMANTIC_SERVICE_URL}


@router.api_route("/api/semantic/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
async def semantic_proxy(path: str, request: Request) -> Response:
    return await forward_request(f"{SEMANTIC_SERVICE_URL}/api/search/{path}", request)


@router.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
async def proxy(path: str, request: Request) -> Response:
    return await forward_request(f"{BACKEND_URL}/api/{path}", request)


async def forward_request(url: str, request: Request) -> Response:
    body = await request.body()
    headers = {
        key: value
        for key, value in request.headers.items()
        if key.lower() not in {"host", "content-length", "origin"}
    }

    async with httpx.AsyncClient(timeout=20.0) as client:
        try:
            backend_response = await client.request(
                request.method,
                url,
                params=request.query_params,
                content=body,
                headers=headers,
            )
        except httpx.HTTPError as exc:
            return JSONResponse(
                status_code=502,
                content={"detail": f"Gateway upstream error: {exc}"},
            )

    excluded_headers = {"content-encoding", "transfer-encoding", "connection"}
    response_headers: dict[str, Any] = {
        key: value
        for key, value in backend_response.headers.items()
        if key.lower() not in excluded_headers
    }
    return Response(
        content=backend_response.content,
        status_code=backend_response.status_code,
        headers=response_headers,
        media_type=backend_response.headers.get("content-type"),
    )
