from fastapi import FastAPI

app = FastAPI(title="Parcel Desk")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}