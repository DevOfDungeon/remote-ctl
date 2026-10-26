import asyncio
from contextlib import asynccontextmanager

import psutil
from fastapi import Depends, FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError

from . import protocol as p
from .auth import require_token, token_ok, locked_out, record_failure
from .backends import get_backend

from pathlib import Path

import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("rc")

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.input = get_backend()
    yield
    app.state.input.close()


app = FastAPI(title="remote-ctl", lifespan=lifespan)


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


@app.websocket("/ws/input")
async def ws_input(ws: WebSocket):
    await ws.accept()
    ip = ws.client.host if ws.client else "unknown"
    if locked_out(ip):
        log.warning("locked out: %s", ip)
        await ws.close(code=4429)
        return
    try:
        first = await asyncio.wait_for(ws.receive_text(), timeout=5)
    except asyncio.TimeoutError:
        await ws.close(code=4408)
        return
    except WebSocketDisconnect:
        log.info("client disconnected: %s", ip)
        return
    if not token_ok(first):
        record_failure(ip)
        log.warning("bad token from %s", ip)
        await ws.close(code=4401)
        return

    await ws.send_text("ok")
    log.info("client connected: %s", ip)

    dev = ws.app.state.input
    try:
        while True:
            raw = await ws.receive_text()
            try:
                msg = p.parse(raw)
            except ValidationError:
                continue
            match msg:
                case p.Move():
                    dev.move(msg.dx, msg.dy)
                case p.Scroll():
                    dev.scroll(msg.dx, msg.dy)
                case p.Click():
                    dev.click(msg.b)
    except WebSocketDisconnect:
        pass

app.mount("/", StaticFiles(directory=Path(__file__).parent / "static", html=True), name="static")