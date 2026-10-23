import uvicorn

from .config import HOST, PORT, TOKEN

if __name__ == "__main__":
    print(f"\n  token: {TOKEN}\n")
    uvicorn.run("agent.main:app", host=HOST, port=PORT)