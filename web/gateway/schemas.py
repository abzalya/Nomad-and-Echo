#Public contract
from typing import Literal, Optional
from pydantic import BaseModel, Field

class MoveRequest(BaseModel):
    fen: str
    history: list[str] = Field(default_factory=list)
    opponent: Literal["nomad", "echo"]
    think_ms: Optional[int] = Field(default=None, ge=1, le=60_000)

class MoveResponse(BaseModel):
    uci: str
    san: str
    eval: Optional[int] = None
    depth: Optional[int] = None
    time_ms: int

class HintRequest(BaseModel):
    fen: str
    history: list[str] = Field(default_factory=list)

class HintResponse(BaseModel):
    uci: str
    san: str

class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    version: str