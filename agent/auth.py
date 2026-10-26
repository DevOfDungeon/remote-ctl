import secrets
import time
from collections import defaultdict

from fastapi import Header, HTTPException, Request

from .config import TOKEN

MAX_FAILS = 5
LOCKOUT_S = 60
_fails: dict[str, list[float]] = defaultdict(list)


def token_ok(candidate: str) -> bool:
    return secrets.compare_digest(candidate.encode(), TOKEN.encode())

def locked_out(ip: str) -> bool:
    now = time.monotonic()
    recent = [t for t in _fails[ip] if now - t < LOCKOUT_S]
    _fails[ip] = recent
    return len(recent) >= MAX_FAILS


def record_failure(ip: str) -> None:
    _fails[ip].append(time.monotonic())


def require_token(request: Request, authorization: str = Header(default="")) -> None:
    ip = request.client.host if request.client else "unknown"
    if locked_out(ip):
        raise HTTPException(status_code=429, detail="too many attempts")
    scheme, _, value = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token_ok(value):
        record_failure(ip)
        raise HTTPException(status_code=401, detail="unauthorized")