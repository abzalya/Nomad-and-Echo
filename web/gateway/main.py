from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from schemas import (
    HealthResponse,
    HintRequest,
    HintResponse,
    MoveRequest,
    MoveResponse,
)
import clients

@asynccontextmanager
async def lifespan(app: FastAPI):
    await clients.startup()
    yield
    await clients.shutdown()

app = FastAPI(title="chess-room gateway", version=settings.version, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

@app.get("/api/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok", version=settings.version)

@app.post("/api/bot/move", response_model=MoveResponse)
async def bot_move(req: MoveRequest) -> MoveResponse:
    think_ms = req.think_ms if req.think_ms is not None else settings.unlimited_think_ms
    try:
        if req.opponent == "nomad":
            result = await clients.nomad_move(req.fen, req.history, think_ms)
        else:
            result = await clients.echo_move(req.fen, req.history)
    except clients.DownstreamError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc
    except (httpx.TimeoutException, httpx.ConnectError) as exc:
        raise HTTPException(status_code=503, detail=f"engine unavailable: {exc}") from exc
    return MoveResponse(**result)

@app.post("/api/hint", response_model=HintResponse)
async def hint(req: HintRequest) -> HintResponse:
    try:
        result = await clients.nomad_move(req.fen, req.history, settings.hint_think_ms)
    except clients.DownstreamError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc
    except (httpx.TimeoutException, httpx.ConnectError) as exc:
        raise HTTPException(status_code=503, detail=f"engine unavailable: {exc}") from exc
    return HintResponse(uci=result["uci"], san=result["san"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
