from fastapi import FastAPI

from app import store
from app.auth import router as auth_router

app = FastAPI(title="Parcel Desk")
app.include_router(auth_router)


@app.on_event("startup")
def initialize_store() -> None:
    store.seed()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
