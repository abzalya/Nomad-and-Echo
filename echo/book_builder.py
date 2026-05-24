import chess
import chess.pgn
import chess.polyglot
import sys
from pathlib import Path
from collections import Counter, defaultdict
import pickle

sys.path.insert(0, str(Path(__file__).parent))
from config import USERNAME

#helpers
def classify_tc(tc:str) -> str | None:
    if not tc: return "unknown"
    if tc.startswith("1/"): return "daily"
    base = int(tc.split("+")[0])
    if base < 180: return "bullet"
    if base < 600: return "blitz"
    return "rapid"

ECHO_ROOT = Path(__file__).parent
ARTIFACTS = ECHO_ROOT / "artifacts"
PGN_PATH = ARTIFACTS / "games_raw.pgn"
OUT_PATH = ARTIFACTS / "echo_book.pkl"

def write_book():
    book: dict[int, Counter[str]] = defaultdict(Counter)
    with open(PGN_PATH) as f:
        while True:
            game = chess.pgn.read_game(f)
            if game is None: break
            if classify_tc(game.headers.get("TimeControl", "")) == "daily":
                continue
            if classify_tc(game.headers.get("TimeControl", "")) == "unknown":
                continue
            if game.headers.get("White", "").lower() == USERNAME: #[White "abzalya"]
                my_colour = chess.WHITE
            elif game.headers.get("Black", "").lower() == USERNAME:
                my_colour = chess.BLACK
            else: continue
            
            #saving the moves
            board = game.board()
            for move in game.mainline_moves():
                if board.turn == my_colour:
                    key = chess.polyglot.zobrist_hash(board)
                    book[key][move.uci()] += 1
                board.push(move)
    with open(OUT_PATH, "wb") as out:
        pickle.dump(dict(book), out)            
            
if __name__ == "__main__":
    write_book()