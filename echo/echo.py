import random
from chess import Board
from echo.book import Book
from echo.config import Config
from pathlib import Path

ECHO_ROOT = Path(__file__).parent
ARTIFACTS = ECHO_ROOT / "artifacts"
BOOK_PATH = ARTIFACTS / "echo_book.pkl"

class Echo:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.book = Book(BOOK_PATH) if cfg.use_book else None

    def choose_move(self, board: Board) -> tuple[str, str]:
        if self.book and (m := self.book.lookup(board)):
            return m, "book"
        #for now, return random move out of book
        return random.choice(list(board.legal_moves)).uci(), "random"
