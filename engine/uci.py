import sys
from core.game import Game
from core.move import MoveFlag
from engine.search import best_move

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
        # bishops → b, queens → q, rooks → r, knights → n
        if move.promo_piece.endswith("Knights"):
            letter = "n"
        uci += letter
    return uci

def uci_loop():
    sys.stdin.reconfigure(encoding='utf-8-sig')
    game = Game()
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
            game = Game()

        elif line.startswith("position"):
            game = Game()
            parts = line.split()
            move_idx = None
            if "moves" in parts:
                move_idx = parts.index("moves")
                moves_list = parts[move_idx + 1:]
            else:
                moves_list = []
            # only startpos supported for now (no FEN parsing)
            for uci in moves_list:
                move = uci_to_move(uci, game.legal_moves, game.gs.whiteToMove)
                if move:
                    game.apply(move)

        elif line.startswith("go"):
            parts = line.split()
            if "depth" in parts:
                depth = int(parts[parts.index("depth") + 1])
            move = best_move(game.gs, depth)
            if move:
                print(f"bestmove {move_to_uci(move)}")
            else:
                print("bestmove 0000")

        elif line == "quit":
            break

        sys.stdout.flush()

if __name__ == "__main__":
    uci_loop()
