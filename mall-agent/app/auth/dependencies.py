from fastapi import Request, HTTPException ,status

from app.auth.auth_client import java_auth_client, JavaAuthError
from app.auth.request_context import (
    reset_authorization,
    set_authorization,
)


async def get_user_context(request:Request):
    """从请求中读取商城 Token，并调用 Java 完成一次鉴权。"""
    authorization = request.headers.get("Authorization")

    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未授权"
        )

    request_id = request.headers.get("X-Request-Id")

    try:
        user_context = await java_auth_client.introspect(
            authorization=authorization,
            request_id=request_id,
        )
    except JavaAuthError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="token检验失败，请重新登录"
        ) from exc

    if not user_context.enabled:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户已被禁用",
        )

    context_token = set_authorization(
        user_context.access_token
    )

    try:
        yield user_context
    finally:
        reset_authorization(context_token)