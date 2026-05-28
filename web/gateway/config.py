import os

class Settings:
    version: str = "0.1"

    def __init__(self) -> None:
        origins = os.environ.get("CORS_ORIGINS", "http://localhost:3000")
        self.cors_origins: list[str] = [o.strip() for o in origins.split(",") if o.strip()]

        #Unlimited mode → 5000 ms / move.
        self.unlimited_think_ms: int = int(os.environ.get("UNLIMITED_THINK_MS", "5000"))
        #Hint always runs Nomad.
        self.hint_think_ms: int = int(os.environ.get("HINT_THINK_MS", "1500"))

        # Downstream engine URLs
        self.nomad_url: str = os.environ.get("NOMAD_URL", "http://localhost:8001")
        self.echo_url: str = os.environ.get("ECHO_URL", "http://localhost:8002")

        # httpx timeout = think_ms + slack so engines have wiggle room.
        self.timeout_slack_ms: int = int(os.environ.get("TIMEOUT_SLACK_MS", "5000"))

settings = Settings()