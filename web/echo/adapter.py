import asyncio
import time
import chess
from typing import Optional

#Echo Imports
from echo.config import Config
from echo.echo import Echo

from config import settings

_lock = asyncio.Lock()
_engine: Optional[Echo] = None
_init_error: Optional[str] = None

async def warmup():
    #spawn lc0 subprocess and load maia weights
    global _engine, _init_error
    cfg = Config(
        use_book=settings.echo_use_book,
        book_only=settings.echo_book_only,
        maia_elo=settings.maia_elo,
    )
    try: 
        _engine = await asyncio.to_thread(Echo, cfg)
    except Exception as exc:
        _init_error = f"{type(exc).__name__}: {exc}"
        _engine = None

async def shutdown() -> None:
    global _engine
    if _engine is not None:
        await asyncio.to_thread(_engine.close)
        _engine = None

def is_ready() -> bool:
    return _engine is not None

def init_error() -> Optional[str]:
    return _init_error

async def pick_move(fen, history):
    async with _lock:
        return await asyncio.to_thread(_pick_move_sync, fen, history)

def _pick_move_sync(fen, history) -> dict:
    if _engine is None:
        raise RuntimeError(f"echo unavailable: {_init_error or 'not initialized'}")

    try:
        board = chess.Board(fen)
    except ValueError as exc:
        raise ValueError(f"invalid fen: {exc}") from exc

    for uci in history:
        try:
            mv = chess.Move.from_uci(uci)
        except ValueError as exc:
            raise ValueError(f"invalid uci in history: {uci}") from exc
        if mv not in board.legal_moves:
            raise ValueError(f"illegal move in history: {uci}")
        board.push(mv)

    if not list(board.legal_moves):
        raise ValueError("no legal moves in this position")

    t0 = time.perf_counter()
    uci, _info = _engine.choose_move(board)
    elapsed_ms = int((time.perf_counter() - t0) * 1000)

    mv = chess.Move.from_uci(uci)
    if mv not in board.legal_moves:
        raise RuntimeError(f"Echo produced an illegal move: {uci}")

    return {
        "uci": uci,
        "san": board.san(mv),
        "eval": None,
        "depth": None,
        "time_ms": elapsed_ms,
    }
