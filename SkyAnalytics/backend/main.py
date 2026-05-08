from fastapi import FastAPI

app = FastAPI(title="SkyAnalytics Backend", version="1.0.0")

@app.get("/")
async def root():
    return {"message": "Welcome to SkyAnalytics Backend"}

@app.get("/health")
async def health():
    return {"status": "healthy"}