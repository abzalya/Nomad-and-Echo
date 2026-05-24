import random
from chess import Board
from echo.book import Book
from echo.config import Config
from pathlib import Path
from echo.maia import Maia

ECHO_ROOT = Path(__file__).parent
ARTIFACTS = ECHO_ROOT / "artifacts"
BOOK_PATH = ARTIFACTS / "echo_book.pkl"

class Echo:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.book = Book(BOOK_PATH) if cfg.use_book else None
        if not cfg.book_only:
            self.maia = Maia(cfg.maia_elo, cfg.lc0_path, cfg.weights_dir) 
        else: self.maia = None
        
    def close(self):
        if self.maia: self.maia.close()

    def choose_move(self, board: Board) -> tuple[str, str]:
        if self.book and (m := self.book.lookup(board)):
            return m, "book"
        if self.maia:
            return self.maia.choose_move(board), "maia"
        return random.choice(list(board.legal_moves)).uci(), "random"
