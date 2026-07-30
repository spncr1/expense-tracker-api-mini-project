from fastapi import FastAPI

from app.auth.router import router as auth_router
from app.core.config import get_settings
from app.expenses.router import router as expenses_router


settings = get_settings()

app = FastAPI(title=settings.app_name)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


app.include_router(auth_router)
app.include_router(expenses_router)
