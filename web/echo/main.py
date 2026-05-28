#Echo service
_ECHO_VERSION = "1.0"

import sys
import pathlib
from contextlib import asynccontextmanager

#repo root to sys.path
_REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from fastapi import FastAPI, HTTPException
from config import settings
from schemas import HealthResponse, MoveRequest, MoveResponse
import adapter

@asynccontextmanager
async def lifespan(app: FastAPI):
    await adapter.warmup()
    yield
    await adapter.shutdown()

app = FastAPI(title="echo", version=_ECHO_VERSION, lifespan=lifespan)

@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok" if adapter.is_ready() else "something is wrong", version = _ECHO_VERSION)

@app.post("/move", response_model=MoveResponse)
async def move(req: MoveRequest) -> MoveResponse:
    if not adapter.is_ready():
        raise HTTPException(status_code=503, detail=f"echo unavailable: {adapter.init_error()}")
    try:
        result = await adapter.pick_move(req.fen, req.history)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return MoveResponse(**result)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=False)