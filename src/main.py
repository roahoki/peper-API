import logging

from fastapi import FastAPI

from src.routers import webhook

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)

app = FastAPI(
    title="WiVer Bot API",
    description="Backend for Peper expense management Telegram bot",
    version="1.0.0",
)

app.include_router(webhook.router)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "WiVer API is up and running :)"}
