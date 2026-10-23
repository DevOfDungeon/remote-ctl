import os
import secrets

TOKEN = os.environ.get("RC_TOKEN") or secrets.token_urlsafe(24)
HOST = os.environ.get("RC_HOST", "127.0.0.1")  # loopback by default: opt in to exposure
PORT = int(os.environ.get("RC_PORT", "8000"))