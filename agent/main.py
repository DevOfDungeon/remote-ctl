import psutil
from fastapi import FastAPI, Depends

from .auth import require_token

app = FastAPI(title="remote-ctl")


@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/stats", dependencies=[Depends(require_token)])
def stats():
    return {
        "cpu": psutil.cpu_percent(),
        "ram": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage("/").percent,
    }