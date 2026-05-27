#Nomad service
_NOMAD_VERSION = "1.0"

import sys
import pathlib
from contextlib import asynccontextmanager

#repo root to sys.path
_REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from fastapi import FastAPI, HTTPException
from schemas import HealthResponse, MoveRequest, MoveResponse
import adapter

@asynccontextmanager
async def lifespan(app: FastAPI):
    await adapter.warmup()
    yield

app = FastAPI(title="nomad", version=_NOMAD_VERSION, lifespan=lifespan)

@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok", version = _NOMAD_VERSION)

@app.post("/move", response_model=MoveResponse)
async def move(req: MoveRequest) -> MoveResponse:
    try:
        result = await adapter.pick_move(req.fen, req.history, req.think_ms)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return MoveResponse(**result)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=False)