from typing import Optional

import httpx

from config import settings


class DownstreamError(Exception):
    def __init__(self, status_code: int, detail: str):
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail

_nomad: Optional[httpx.AsyncClient] = None
_echo: Optional[httpx.AsyncClient] = None

async def startup():
    global _nomad, _echo
    _nomad = httpx.AsyncClient(base_url=settings.nomad_url, timeout=None)
    _echo = httpx.AsyncClient(base_url=settings.echo_url, timeout=None)

async def shutdown():
    global _nomad, _echo
    if _nomad is not None:
        await _nomad.aclose()
        _nomad = None
    if _echo is not None:
        await _echo.aclose()
        _echo = None

def _timeout_for(think_ms: int) -> float:
    return (think_ms + settings.timeout_slack_ms) / 1000

async def nomad_move(fen, history, think_ms):
    assert _nomad is not None
    r = await _nomad.post(
        "/move",
        json={"fen": fen, "history": history, "think_ms": think_ms},
        timeout=_timeout_for(think_ms),
    )
    _raise_for_status(r)
    return r.json()

async def echo_move(fen, history):
    assert _echo is not None
    r = await _echo.post(
        "/move",
        json={"fen": fen, "history": history},
        timeout=_timeout_for(2000),
    )
    _raise_for_status(r)
    return r.json()

def _raise_for_status(r: httpx.Response):
    if r.status_code >= 400:
        try:
            detail = r.json().get("detail", r.text)
        except Exception:
            detail = r.text
        raise DownstreamError(r.status_code, detail)
