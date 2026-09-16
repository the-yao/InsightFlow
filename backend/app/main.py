from fastapi import FastAPI

from app.api.datasets import router as datasets_router

app = FastAPI(title="InsightFlow")

app.include_router(datasets_router)


@app.get("/health")
def health():
    return {"status": "ok"}