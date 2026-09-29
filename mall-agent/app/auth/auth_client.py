from dataclasses import dataclass
from typing import Any

import httpx

from app.core.config import settings


class JavaAuthError(Exception):
    """Java 鉴权接口返回失败时抛出的异常。"""


@dataclass(frozen=True)
class UserContext:
    """商城用户鉴权上下文。"""

    user_id: str
    shop_id: int | None
    sys_type: int | None
    is_admin: int | None
    biz_user_id: str | None
    perms: set[str]
    enabled: bool
    other_id: int | None
    access_token: str


class JavaAuthClient:
    """调用 Java 内部鉴权接口，校验商城 Authorization。"""

    def __init__(
        self,
        introspect_url: str,
        service_token: str,
        timeout: float = 5.0,
    ) -> None:
        self._introspect_url = introspect_url
        self._service_token = service_token
        self._timeout = timeout

    async def introspect(
        self,
        authorization: str,
        request_id: str | None = None,
    ) -> UserContext:
        """调用 Java 鉴权接口并返回用户上下文。"""
        if not authorization:
            raise JavaAuthError("Authorization header is missing")

        headers = {
            "Authorization": authorization,
            "X-Mall-Agent-Token": self._service_token,
        }

        if request_id:
            headers["X-Request-Id"] = request_id

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(
                    self._introspect_url,
                    headers=headers,
                )
        except httpx.HTTPError as exc:
            raise JavaAuthError("Java auth service is unavailable") from exc

        try:
            payload: dict[str, Any] = response.json()
        except ValueError as exc:
            raise JavaAuthError("Invalid response from Java auth service") from exc

        if response.status_code >= 400:
            raise JavaAuthError("Java auth service rejected the request")

        if payload.get("code") != "00000":
            raise JavaAuthError(
                payload.get("msg") or "商城 Token 校验失败"
            )

        data = payload.get("data")
        if not isinstance(data, dict):
            raise JavaAuthError("Java auth response data is invalid")

        return UserContext(
            user_id=str(data["userId"]),
            shop_id=data.get("shopId"),
            sys_type=data.get("sysType"),
            is_admin=data.get("isAdmin"),
            biz_user_id=data.get("bizUserId"),
            perms=set(data.get("perms") or []),
            enabled=bool(data.get("enabled")),
            other_id=data.get("otherId"),
            access_token=authorization,
        )


java_auth_client = JavaAuthClient(
    introspect_url=settings.JAVA_AUTH_INTROSPECT_URL,
    service_token=settings.MALL_AGENT_AUTH_TOKEN,
)