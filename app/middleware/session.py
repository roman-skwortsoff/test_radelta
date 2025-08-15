import uuid
from fastapi import Request


async def session_key_middleware(request: Request, call_next):
    if "session_id" not in request.cookies:
        session_key = str(uuid.uuid4())
        response = await call_next(request)
        response.set_cookie(
            key="session_id",
            value=session_key,
            max_age=60 * 60 * 24 * 365 * 10,  # 10 лет
            httponly=True,
            samesite="lax",
        )
        return response
    else:
        response = await call_next(request)
        return response
