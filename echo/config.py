import os
import platform
from dataclasses import dataclass, field
from pathlib import Path

ECHO_ROOT = Path(__file__).parent
ARTIFACTS = ECHO_ROOT / "artifacts"

USERNAME = "abzalya"


def _default_lc0_path() -> Path:
    env = os.environ.get("LC0_PATH")
    if env:
        return Path(env)
    #windows dev uses lc0.exe, linux containers use bare lc0
    binary = "lc0.exe" if platform.system() == "Windows" else "lc0"
    return ECHO_ROOT / "bin" / binary


def _default_weights_dir() -> Path:
    env = os.environ.get("WEIGHTS_DIR")
    return Path(env) if env else ARTIFACTS / "weights"


@dataclass
class Config:
    use_book: bool = True
    book_only: bool = False
    maia_elo: int = 1700
    lc0_path: Path = field(default_factory=_default_lc0_path)
    weights_dir: Path = field(default_factory=_default_weights_dir)

    def apply_setoption(self, line: str):
        parts = line.split()
        name, value = parts[2], parts[4]
        if name == "UseBook":
            self.use_book = value.lower() == "true"
        elif name == "BookOnly":
            self.book_only = value.lower() == "true"
        elif name == "MaiaElo":
            self.maia_elo = int(value)
