from fastapi import FastAPI

app = FastAPI(
    title="Mall Agent Api",
    description="Mall Agent API",
    version="1.0",
)

@app.get("/health")
def health():
    return {"status": "ok"}