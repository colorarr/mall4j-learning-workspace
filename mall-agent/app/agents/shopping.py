from langchain.agents import create_agent
from langchain.agents.middleware import (
    ModelCallLimitMiddleware,
    ModelRetryMiddleware,
    ToolCallLimitMiddleware,
    ToolRetryMiddleware,
)

from app.agents.tool_policy import (
    SHOPPING_TOOL_POLICIES,
    get_retryable_tool_names,
)
from app.core.llm import get_glm_model
from app.mcp.client import load_current_user_tools


async def get_shopping_agent():
    """创建商城导购智能体。"""
    product_tools = await load_current_user_tools(
        "product_"
    )

    # 获取可重试工具名单
    retryable_tool_names = get_retryable_tool_names(
        SHOPPING_TOOL_POLICIES,
    )

    # 定义模型调用次数的中间件
    model_call_limit = ModelCallLimitMiddleware(
        run_limit=8,
        exit_behavior="end",
    )

    # 定义工具调用次数的中间件
    tool_call_limit = ToolCallLimitMiddleware(
        run_limit=12,
        exit_behavior="end",
    )

    # 定义工具重试的中间件
    tool_retry_middleware = ToolRetryMiddleware(
        tools=retryable_tool_names,
        max_retries=2,
        initial_delay=1.0,
        backoff_factor=2.0,
        max_delay=8.0,
        jitter=True,
        on_failure="continue",
    )

    # 定义模型重试的中间件
    model_retry_middleware = ModelRetryMiddleware(
        max_retries=2,
        initial_delay=1.0,
        backoff_factor=2.0,
        max_delay=8.0,
        jitter=True,
        on_failure="error",
    )

    return create_agent(
        name="shopping_agent",
        model=get_glm_model(),
        tools=product_tools,
        middleware=[
            model_call_limit,
            tool_call_limit,
            model_retry_middleware,
            tool_retry_middleware,
        ],
        system_prompt="""
        你是商城购物导购智能体，负责帮助用户发现和选择商品。

        工作要求：
        - 理解用户的品类、用途、预算、风格、规格和其他偏好。
        - 需要商品数据时调用商品搜索、详情、库存或对比工具；没有工具结果时，不得编造商品、价格、库存、评分或优惠信息。
        - 推荐商品时说明与用户需求的匹配理由，并指出仍然缺少的关键信息。
        - 信息不足时提出一到两个简短的澄清问题，不要一次询问过多问题。
        - 比较商品时，从价格、核心参数、适用场景和限制进行客观比较。
        - 用户表达购买意向时，可以引导查看详情或加入购物车；没有明确请求时，不要修改购物车或提交订单。

        边界要求：
        - 只处理商品发现、商品详情、商品推荐和商品对比。
        - 不要回答订单、售后或与商城无关的问题，应交给上层路由或对应业务智能体。
        - 使用中文，回答简洁、具体、易于扫描。
        """
    )
