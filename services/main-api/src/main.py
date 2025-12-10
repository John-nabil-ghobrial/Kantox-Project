import os
import logging
from typing import Any, Dict, List

import httpx
from fastapi import FastAPI, HTTPException, Request

# --------------------------------------------------------------------
# Basic configuration
# --------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main-api")

MAIN_API_VERSION = os.getenv("APP_VERSION", "dev")
AUX_BASE_URL = os.getenv(
    "AUX_BASE_URL",
    # Default: Kubernetes DNS for aux-service Service
    "http://aux-service.aux-service.svc.cluster.local:8000",
)

app = FastAPI(
    title="Main API",
    description="Public API for the Kontaxa challenge. Delegates AWS calls to aux-service.",
    version=MAIN_API_VERSION,
)


# --------------------------------------------------------------------
# HTTP client setup (reuse one client for performance)
# --------------------------------------------------------------------
@app.on_event("startup")
async def startup_event():
    app.state.http_client = httpx.AsyncClient(timeout=5.0)


@app.on_event("shutdown")
async def shutdown_event():
    client: httpx.AsyncClient = app.state.http_client
    await client.aclose()


async def _get_aux_client(request: Request) -> httpx.AsyncClient:
    return request.app.state.http_client


# --------------------------------------------------------------------
# Helpers: versions + error handling
# --------------------------------------------------------------------
async def _get_aux_version(client: httpx.AsyncClient) -> str:
    try:
        resp = await client.get(f"{AUX_BASE_URL}/version")
        resp.raise_for_status()
        data = resp.json()
        return data.get("version", "unknown")
    except Exception as exc:
        logger.exception("Failed to get aux-service version")
        # We still respond, but mark aux version as unknown
        return f"unreachable ({exc.__class__.__name__})"


async def _wrap_with_versions(
    request: Request,
    data: Any,
) -> Dict[str, Any]:
    """
    Wrap any response payload with version metadata for both services.
    This satisfies the requirement:
      - Every API response must include version of Main API and Auxiliary Service.
    """
    client = await _get_aux_client(request)
    aux_version = await _get_aux_version(client)
    return {
        "data": data,
        "mainApiVersion": MAIN_API_VERSION,
        "auxServiceVersion": aux_version,
    }


async def _proxy_get(
    request: Request,
    aux_path: str,
) -> Dict[str, Any]:
    """
    Helper to call aux-service and wrap the result with versions.
    """
    client = await _get_aux_client(request)
    try:
        url = f"{AUX_BASE_URL}{aux_path}"
        logger.info("Calling aux-service: %s", url)
        resp = await client.get(url)
        resp.raise_for_status()
        payload = resp.json()
    except httpx.HTTPStatusError as exc:
        logger.exception("Aux-service returned error")
        # propagate aux-service error status code & message
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    except httpx.RequestError as exc:
        logger.exception("Failed to reach aux-service")
        raise HTTPException(status_code=502, detail=f"Error calling aux-service: {exc}")

    return await _wrap_with_versions(request, payload)


# --------------------------------------------------------------------
# Health & version
# --------------------------------------------------------------------
@app.get("/health")
async def health(request: Request) -> Dict[str, Any]:
    return await _wrap_with_versions(
        request,
        {"status": "ok", "service": "main-api"},
    )


@app.get("/version")
async def version(request: Request) -> Dict[str, Any]:
    return await _wrap_with_versions(
        request,
        {"service": "main-api"},
    )


# --------------------------------------------------------------------
# Business endpoints (required by the challenge)
# --------------------------------------------------------------------
@app.get("/buckets")
async def list_buckets(request: Request) -> Dict[str, Any]:
    """
    List all S3 buckets in the AWS account.
    Delegates S3 call to aux-service.
    """
    return await _proxy_get(request, "/aws/buckets")


@app.get("/parameters")
async def list_parameters(request: Request) -> Dict[str, Any]:
    """
    List all parameters stored in AWS Parameter Store.
    Delegates SSM call to aux-service.
    """
    return await _proxy_get(request, "/aws/parameters")


@app.get("/parameters/{name}")
async def get_parameter(name: str, request: Request) -> Dict[str, Any]:
    """
    Retrieve the value of a specific parameter from AWS Parameter Store.
    Delegates SSM call to aux-service.
    """
    return await _proxy_get(request, f"/aws/parameters/{name}")


# --------------------------------------------------------------------
# Uvicorn entrypoint
# --------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=False,
    )
