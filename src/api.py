import os
import sys
import uuid
import time
import json
import datetime
from contextlib import asynccontextmanager

import uvicorn

import fastapi
from fastapi import Request, Security
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security.api_key import APIKey, APIKeyHeader
from starlette.status import (
    HTTP_200_OK,
    HTTP_404_NOT_FOUND,
    HTTP_422_UNPROCESSABLE_ENTITY,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

import docs
import utils
import config
import version

api_key_header = APIKeyHeader(name=config.API_KEY_NAME)


@asynccontextmanager
async def lifespan(app: fastapi.FastAPI):
    utils.log({"body": "API Service Started", "context": "startup_event"})
    yield
    utils.log({"body": "API Service Stopped", "context": "shutdown_event"})


app = fastapi.FastAPI(
    title=config.API_TITLE,
    version=config.API_VERSION,
    openapi_tags=docs.ENDPOINT_TAGS,
    description=docs.DESCRIPTION,
    lifespan=lifespan,
)

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_context(request: Request, call_next):
    """Middleware that processes every request and response"""
    start_time = time.time()
    request.state.request_id = request.query_params.get("request_id", str(uuid.uuid4()))

    body = None
    if request.method == "POST":
        try:
            body = await request.json()
        except:
            pass

    headers_to_log = {
        k: v for k, v in request.headers.items() if k.lower() != "x-api-key"
    }

    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = f"{process_time:0.6f}"
    response.headers["request_id"] = request.state.request_id
    response.headers["api_version"] = version.__version__
    request_info = {
        "request_id": request.state.request_id,
        "method": request.method,
        "path": request.url.path,
        "status_code": response.status_code,
        "process_time": f"{process_time:0.6f}",
        "headers": headers_to_log,
        "json_payload": body,
    }
    utils.log(f"Request received:\n{json.dumps(request_info, indent=4)}")
    return response


@app.get("/health")
def health():
    return JSONResponse(content={"status": "available"}, status_code=HTTP_200_OK)


@app.get("/ping", summary="Ping", tags=["ping"])
async def ping(request: Request, api_key: APIKey = Security(api_key_header)):
    """
    Health check with API KEY

    Args:
        request (Request): HTTP request
        api_key (APIKey): API key

    Returns:
        HTTP JSON response
    """
    utils.log(f"Ping endpoint requested by {request.state.request_id}")
    message = {
        "id": request.state.request_id,
        "timestamp": str(utils.now()),
        "body": "Ping endpoint requested.",
        "metadata": {
            "request_id": str(request.state.request_id),
            "client_host": str(request.client.host),
            "request_headers": str(request.headers.raw),
        },
    }
    utils.log(message)
    return {"ping": "pong", "request_id": request.state.request_id}


api_v1 = fastapi.FastAPI(
    title="V1 API",
    summary=f"V1 API {version.__version__}",
    openapi_tags=docs.ENDPOINT_TAGS,
    description=docs.DESCRIPTION,
    version=version.__version__,
    swagger_ui_parameters={
        "syntaxHighlight.theme": "obsidian",
        "defaultModelsExpandDepth": -1,
    },
    json_schema_extra=None,
)

api_v1.add_middleware(GZipMiddleware, minimum_size=1000)
api_v1.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@api_v1.get(
    "/env",
    tags=["Healthchecks"],
    include_in_schema=True,
    summary="Simple endpoint to view the environment variables currently set - will expose secrets",
)
async def environment(api_key: APIKey = Security(api_key_header)):
    return os.environ


@api_v1.get("/ping", tags=["Healthchecks"], summary="Ping - Check if API is responding")
async def ping(request: Request):
    utils.log(f"Ping endpoint requested by {request.state.request_id}")
    message = {
        "id": str(uuid.uuid4()),
        "timestamp": str(datetime.datetime.utcnow()),
        "body": "Ping endpoint requested.",
        "metadata": {
            "request_id": str(request.state.request_id),
            "client_host": str(request.client.host),
            "request_headers": str(request.headers.raw),
        },
    }
    utils.log(json.dumps(message, indent=4))
    return {"ping": "pong"}


app.mount("/api/v1", api_v1)
# app.mount("/static", StaticFiles(directory="static"), name="static")


if __name__ == "__main__":
    import uvicorn

    utils.log("Starting directly...")
    try:
        uvicorn.run(
            "api:app",
            host="0.0.0.0",
            port=int(os.getenv("API_PORT", 8081)),
            reload=False,
            use_colors=True,
        )
    except Exception as e:
        error = json.dumps(utils.get_exception_details(), indent=4)
        utils.log(f"Error:\n{error}")
        sys.exit(1)
