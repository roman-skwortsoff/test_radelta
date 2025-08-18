import uuid
from fastapi import Request


async def session_key_middleware(request: Request, call_next):
    if "session_id" not in request.cookies:
        request.state.session_id = str(uuid.uuid4())
    else:
        request.state.session_id = request.cookies["session_id"]

    response = await call_next(request)

    if "session_id" not in request.cookies:
        response.set_cookie(
            key="session_id",
            value=request.state.session_id,
            max_age=60 * 60 * 24 * 365 * 10,
            httponly=True,
            samesite="lax",
        )
    return response
