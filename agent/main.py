from fastapi import FastAPI

app = FastAPI(title="remote-ctl")


@app.get("/health")
def health():
    return {"status": "ok"}