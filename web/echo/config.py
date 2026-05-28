import os

class Settings:
    def __init__(self) -> None:
        self.maia_elo: int = int(os.environ.get("MAIA_ELO", "1700"))
        self.echo_use_book: bool = os.environ.get("ECHO_USE_BOOK", "true").lower() == "true"
        self.echo_book_only: bool = os.environ.get("ECHO_BOOK_ONLY", "false").lower() == "true"

settings = Settings()
