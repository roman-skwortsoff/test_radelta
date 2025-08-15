from fastapi import Request
from fastapi.responses import JSONResponse
from app.config import settings


async def api_key_middleware(request: Request, call_next):
    api_key = request.headers.get("X-API-Key")
    if api_key != settings.API_KEY:
        return JSONResponse(status_code=401, content={"detail": "Invalid API key"})
    response = await call_next(request)
    return response
