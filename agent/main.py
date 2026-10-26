import asyncio
from contextlib import asynccontextmanager

import psutil
from fastapi import Depends, FastAPI, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from . import protocol as p
from .auth import require_token, token_ok
from .backends import get_backend


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
    try:
        first = await asyncio.wait_for(ws.receive_text(), timeout=5)
    except asyncio.TimeoutError:
        await ws.close(code=4408)
        return
    except WebSocketDisconnect:
        return
    if not token_ok(first):
        await ws.close(code=4401)
        return

    await ws.send_text("ok")
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
                    print("moving", msg.dx, msg.dy)   # temporary, remove later
                    dev.move(msg.dx, msg.dy)
    except WebSocketDisconnect:
        pass