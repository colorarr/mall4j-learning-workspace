from app.core.config import settings


# Keep Redis Stack support for development; the deployed host uses plain Redis
# and selects SQLite without changing the shared cache service.
if settings.CHECKPOINT_BACKEND == "sqlite":
    from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

    checkpointer = AsyncSqliteSaver.from_conn_string(settings.LANGGRAPH_SQLITE_PATH)
else:
    from langgraph.checkpoint.redis import AsyncRedisSaver

    checkpointer = AsyncRedisSaver(redis_url=settings.REDIS_URL)
