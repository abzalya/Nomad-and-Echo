#API contract pydantic models for Nomad
from typing import Annotated, Optional
from pydantic import BaseModel, Field

#uci move is 5 chars max (e7e8q), cap loosely
UciStr = Annotated[str, Field(max_length=10)]

class MoveRequest(BaseModel):
    fen: str = Field(max_length=120)
    history: list[UciStr] = Field(default_factory=list, max_length=600)
    think_ms: int = Field(ge=1, le=60000)

class MoveResponse(BaseModel):
    uci: str
    san: str
    eval: Optional[int] = None
    depth: Optional[int] = None
    time_ms: int

class HealthResponse(BaseModel):
    status: str
    version: str
