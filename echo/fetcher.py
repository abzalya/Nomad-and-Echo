import sys
import time
import requests
from datetime import datetime, timezone
from pathlib import Path

# works with both run and import `echo.fetcher`
sys.path.insert(0, str(Path(__file__).parent))
from config import USERNAME

ECHO_ROOT = Path(__file__).parent
ARTIFACTS = ECHO_ROOT / "artifacts"
OUT_PATH = ARTIFACTS / "games_raw.pgn"
LAST_FETCHED_PATH = ARTIFACTS / ".last_fetched"

#CHESS.COM API
ARCHIVES_URL = f"https://api.chess.com/pub/player/{USERNAME}/games/archives"
HEADERS = {"User-Agent": f"Echo-mimic-bot abzalamirbay@gmail.com"}


#helpers

def _read_last_fetched() -> str | None:
    if LAST_FETCHED_PATH.exists():
        return LAST_FETCHED_PATH.read_text().strip() or None
    return None


def _write_last_fetched(yyyy_mm: list[str]) -> None:
    LAST_FETCHED_PATH.write_text("/".join(yyyy_mm))


def _is_current_month(yyyy_mm: list[str]) -> bool:
    now = datetime.now(timezone.utc)
    return yyyy_mm == [str(now.year), f"{now.month:02d}"]


def _get_with_backoff(url: str) -> requests.Response:
    """GET with exponential backoff on 429."""
    delay = 1
    for _ in range(4):
        resp = requests.get(url, headers=HEADERS)
        if resp.status_code == 429:
            print(f"[fetcher] 429 — backing off {delay}s", flush=True)
            time.sleep(delay)
            delay *= 2
            continue
        resp.raise_for_status()
        return resp
    raise RuntimeError(f"Gave up fetching {url} after retries")


#main entry

def fetch_all() -> None:
    ARTIFACTS.mkdir(exist_ok=True)

    archives: list[str] = _get_with_backoff(ARCHIVES_URL).json()["archives"]
    last = _read_last_fetched()
    print(f"[fetcher] {len(archives)} monthly archives found; last fetched: {last or 'none'}")

    new_games = 0
    with open(OUT_PATH, "a") as out:
        for archive_url in archives:
            yyyy_mm = archive_url.rsplit("/", 2)[-2:]          #["2024", "12"]
            if last and yyyy_mm <= last.split("/"):
                continue

            print(f"[fetcher] {'/'.join(yyyy_mm)} ...", flush=True)
            games = _get_with_backoff(archive_url).json().get("games", [])

            for g in games:
                #skip variants
                if g.get("rules", "chess") != "chess":
                    continue
                pgn = g.get("pgn", "").strip()
                if pgn:
                    out.write(pgn + "\n\n")
                    new_games += 1

            if not _is_current_month(yyyy_mm):
                _write_last_fetched(yyyy_mm)

            time.sleep(1.0)

    print(f"[fetcher] done -- {new_games} games appended to {OUT_PATH}")


if __name__ == "__main__":
    fetch_all()
