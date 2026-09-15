from fastapi import FastAPI

app = FastAPI(title="InsightFlow")


@app.get("/health")
def health():
    return {"status": "ok"}