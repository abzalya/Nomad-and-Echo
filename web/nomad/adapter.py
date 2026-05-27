import asyncio
import time
import chess

#Nomad Imports
from nomad.core.game import Game
from nomad.core.board import gamestate_from_fen
from nomad.core.move_generator import legalMoves
from nomad.engine.search import iterative_deepening, _Info
from nomad.engine.uci import uci_to_move, move_to_uci

_lock = asyncio.Lock()

async def warmup():
    await asyncio.to_thread(_warmup_sync) #warmup the engine

def _warmup_sync():
    gs = gamestate_from_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    iterative_deepening(gs, soft_time_limit=0.1, info=_Info(0.1))

async def pick_move(fen, history, think_ms):
    async with _lock:
        return await asyncio.to_thread(_pick_move_sync, fen, history, think_ms)

def _pick_move_sync(fen, history, think_ms) -> dict:
    #Fen validation using python-chess
    try:
        board = chess.Board(fen)
    except ValueError as exc:
        raise ValueError(f"invalid fen: {exc}") from exc
    
    game = Game()
    game.gs = gamestate_from_fen(fen)
    game.legal_moves = legalMoves(game.gs)

    for uci in history:
        try:
            mv = chess.Move.from_uci(uci)
        except ValueError as exc:
            raise ValueError(f"invalid uci in history: {uci}") from exc
        if mv not in board.legal_moves:
            raise ValueError(f"illegal move in history: {uci}")
        board.push(mv)

        move = uci_to_move(uci, game.legal_moves, game.gs.whiteToMove)
        if move is None:
            raise ValueError(f"Nomad refused move in history: {uci}")
        game.apply(move)

    if not list(board.legal_moves):
        raise ValueError("no legal moves in this position")

    info = _Info(think_ms / 1000)
    t0 = time.perf_counter()
    best = iterative_deepening(game.gs, soft_time_limit=think_ms / 1000, info=info)
    elapsed_ms = int((time.perf_counter() - t0) * 1000)

    if best is None:
        raise RuntimeError("Nomad returned no move")

    uci = move_to_uci(best)
    mv = chess.Move.from_uci(uci)
    if mv not in board.legal_moves:
        raise RuntimeError(f"Nomad produced an illegal move: {uci}")

    return {
        "uci": uci,
        "san": board.san(mv),
        "eval": int(info.last_score) if info.last_depth > 0 else None,
        "depth": int(info.last_depth) if info.last_depth > 0 else None,
        "time_ms": elapsed_ms,
    }
