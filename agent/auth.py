import secrets

from fastapi import Header, HTTPException

from .config import TOKEN


def token_ok(candidate: str) -> bool:
    # constant-time compare, on bytes so non-ASCII input can't raise
    return secrets.compare_digest(candidate.encode(), TOKEN.encode())


def require_token(authorization: str = Header(default="")) -> None:
    scheme, _, value = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token_ok(value):
        raise HTTPException(status_code=401, detail="unauthorized")