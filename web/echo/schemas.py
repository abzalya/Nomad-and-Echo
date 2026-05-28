#API contract pydantic models for Echo
from typing import Optional
from pydantic import BaseModel, Field

class MoveRequest(BaseModel):
    fen: str
    history: list[str] = Field(default_factory=list)

class MoveResponse(BaseModel):
    uci: str
    san: str
    eval: Optional[int] = None
    depth: Optional[int] = None
    time_ms: int

class HealthResponse(BaseModel):
    status: str
    version: str
