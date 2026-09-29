from contextvars import ContextVar, Token


_authorization_context: ContextVar[str | None] = ContextVar(
    "authorization_context",
    default=None,
)


def set_authorization(
    authorization: str,
) -> Token:
    """绑定当前请求的商城 Token。"""
    return _authorization_context.set(authorization)


def get_authorization() -> str:
    """获取当前请求的商城 Token。"""
    authorization = _authorization_context.get()

    if not authorization:
        raise RuntimeError("当前请求没有商城用户 Token")

    return authorization


def reset_authorization(
    context_token: Token,
) -> None:
    """请求结束后恢复上下文。"""
    _authorization_context.reset(context_token)