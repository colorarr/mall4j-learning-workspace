from langgraph.checkpoint.redis import AsyncRedisSaver

from app.core.config import settings

redis_checkpointer = AsyncRedisSaver(
    redis_url=settings.LANGGRAPH_REDIS_URL,
    ttl={
        "default_ttl":10080,
        "refresh_on_read":True,
    }
)