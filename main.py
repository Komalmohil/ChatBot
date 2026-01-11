from fastapi import FastAPI
from routers.chat import router as chat_router

app = FastAPI(title="Keka Assist", version="1.0.0")

app.include_router(chat_router, prefix="/api", tags=["chat"])