from fastapi import FastAPI

# Initialize the FastAPI app with some metadata for the docs
app = FastAPI(
    title="WiVer Bot API",
    description="Backend for Peper expense management Telegram bot",
    version="1.0.0"
)

# The health endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "message": "WiVer API is up and running :)"
    }