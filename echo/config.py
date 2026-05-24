from dataclasses import dataclass
from pathlib import Path

ECHO_ROOT = Path(__file__).parent
ARTIFACTS = ECHO_ROOT / "artifacts"

USERNAME = "abzalya"

@dataclass
class Config:
    use_book: bool = True
    book_only: bool = False
    MaiaElo: int = 1500

    def apply_setoption(self, line: str):
        parts = line.split()
        name, value = parts[2], parts[4]
        if name == "UseBook":
            self.use_book = value.lower() == "true"
        elif name == "BookOnly":
            self.book_only = value.lower() == "true"
        elif name == "MaiaElo":
            self.MaiaElo = int(value)
