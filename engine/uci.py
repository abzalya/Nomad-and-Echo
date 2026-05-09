import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from core.game import Game
from core.move import MoveFlag
from engine.search import best_move, iterative_deepening, _Info
from engine.tt import tt_clear

FILES = "abcdefgh"

def sq_to_uci(sq):
    return FILES[sq % 8] + str(sq // 8 + 1)

def uci_to_sq(s):
    return (int(s[1]) - 1) * 8 + FILES.index(s[0])

PROMO_LETTER = {"q": "Queens", "r": "Rooks", "b": "Bishops", "n": "Knights"}

def uci_to_move(uci, legal_moves, white_to_move):
    from_sq = uci_to_sq(uci[0:2])
    to_sq   = uci_to_sq(uci[2:4])
    promo   = uci[4] if len(uci) == 5 else None
    color   = "white" if white_to_move else "black"

    for m in legal_moves:
        if m.from_sq != from_sq or m.to_sq != to_sq:
            continue
        if promo:
            if m.promo_piece == color + PROMO_LETTER[promo]:
                return m
        else:
            if not (m.flags & MoveFlag.PROMOTION):
                return m
    return None

def move_to_uci(move):
    uci = sq_to_uci(move.from_sq) + sq_to_uci(move.to_sq)
    if move.flags & MoveFlag.PROMOTION:
        letter = move.promo_piece.replace("white", "").replace("black", "").lower()[0]
        if move.promo_piece.endswith("Knights"):
            letter = "n"
        uci += letter
    return uci

def _get(parts, name, default=None):
    if name in parts:
        return int(parts[parts.index(name) + 1])
    return default

def _allocate_time(remaining_ms, inc_ms, movestogo=None):
    mtg = movestogo if movestogo else 30
    t   = remaining_ms / mtg + inc_ms * 0.8
    t   = min(t, remaining_ms * 0.8)
    return t / 1000  # seconds

_LARGE_DEPTH = 64  # sentinel for time-limited searches

def uci_loop():
    sys.stdin.reconfigure(encoding='utf-8-sig')
    game  = Game()
    depth = 3

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        if line == "uci":
            print("id name Nomad")
            print("id author Abzal Amirbay")
            print("uciok")

        elif line == "isready":
            print("readyok")

        elif line == "ucinewgame":
            game  = Game()
            depth = 3
            tt_clear()

        elif line.startswith("position"):
            game  = Game()
            parts = line.split()
            if "moves" in parts:
                moves_list = parts[parts.index("moves") + 1:]
            else:
                moves_list = []
            # only startpos supported (no FEN parsing yet)
            for uci in moves_list:
                move = uci_to_move(uci, game.legal_moves, game.gs.whiteToMove)
                if move:
                    game.apply(move)

        elif line.startswith("go"):
            parts      = line.split()
            time_limit = None
            search_depth = depth

            if "depth" in parts:
                search_depth = _get(parts, "depth")

            elif "movetime" in parts:
                time_limit   = _get(parts, "movetime") / 1000  # ms → s
                search_depth = _LARGE_DEPTH

            elif "wtime" in parts or "btime" in parts:
                wtime = _get(parts, "wtime", 0)
                btime = _get(parts, "btime", 0)
                winc  = _get(parts, "winc",  0)
                binc  = _get(parts, "binc",  0)
                mtg   = _get(parts, "movestogo")
                remaining = wtime if game.gs.whiteToMove else btime
                inc       = winc  if game.gs.whiteToMove else binc
                time_limit   = _allocate_time(remaining, inc, mtg)
                search_depth = _LARGE_DEPTH

            elif "infinite" in parts:
                search_depth = _LARGE_DEPTH  # runs until 'stop' (not yet supported)

            if time_limit is not None:
                move = iterative_deepening(game.gs, time_limit)
            else:
                move = best_move(game.gs, search_depth, _Info(None))
            print(f"bestmove {move_to_uci(move) if move else '0000'}")

        elif line == "quit":
            break

        sys.stdout.flush()

if __name__ == "__main__":
    uci_loop()
