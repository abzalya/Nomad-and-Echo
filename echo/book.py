import pickle
import random
from chess import Board, polyglot, Move


class Book:
    def __init__(self, path):
        with open(path, "rb") as f:
            self.data: dict = pickle.load(f)

    def lookup(self, board: Board) -> str | None:
        key = polyglot.zobrist_hash(board)
        moves = self.data.get(key)
        if not moves:
            return None
        choices, weights = zip(*moves.items())
        pick = random.choices(choices, weights=weights, k=1)[0]
        if Move.from_uci(pick) in board.legal_moves:
            return pick
        return None
