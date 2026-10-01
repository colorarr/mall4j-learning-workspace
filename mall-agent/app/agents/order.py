from langchain.agents import create_agent
from langchain.agents.middleware import (
    HumanInTheLoopMiddleware,
    ModelCallLimitMiddleware,
    ModelRetryMiddleware,
    ToolCallLimitMiddleware,
    ToolRetryMiddleware,
)

from app.agents.tool_policy import (
    ORDER_TOOL_POLICIES,
    get_approval_tool_names,
    get_retryable_tool_names,
)
from app.core.llm import get_glm_model
from app.mcp.client import load_current_user_tools


async def get_order_agent():
    """创建当前请求对应的订单智能体。"""
    order_tools = await load_current_user_tools(
        "order_",
    )

    # 获取可重试工具名单
    retryable_tool_names = get_retryable_tool_names(
        ORDER_TOOL_POLICIES,
    )

    # 获取需要人工介入的工具名称
    approval_tool_names = get_approval_tool_names(
        ORDER_TOOL_POLICIES,
    )

    approval_descriptions = {
        "order_cancel": "将取消选中的订单，批准后立即执行。",
        "order_confirm_receipt": "将确认选中的订单已经收货，批准后立即执行。",
        "order_delete_history": "将删除选中的历史订单记录，批准后立即执行。",
    }

    # 定义人工介入中间件
    human_in_the_loop_middleware = HumanInTheLoopMiddleware(
        interrupt_on={
            tool_name: {
                "allowed_decisions": [
                    "approve",
                    "reject",
                ],
                "description": approval_descriptions.get(
                    tool_name,
                    "该操作会修改订单数据，批准后立即执行。",
                ),
            }
            for tool_name in approval_tool_names
        },
        description_prefix="订单操作需要用户确认",
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
        name="order_agent",
        model=get_glm_model(),
        tools=order_tools,
        middleware=[
            model_call_limit,
            tool_call_limit,
            model_retry_middleware,
            tool_retry_middleware,
            human_in_the_loop_middleware,
        ],
        system_prompt="""
你是商城订单智能体，负责帮助用户查询和管理自己的订单。

工作要求：
- 处理订单列表、订单详情、订单状态、物流信息和订单相关操作。
- 当用户没有提供订单号时，先查询订单列表或询问必要信息，不要猜测订单。
- 需要订单、物流或售后状态时，必须调用对应工具；没有工具结果时，不得编造订单号、金额、状态、物流节点或时间。
- 对取消订单、确认收货和删除历史订单等操作，必须先确保目标订单已经明确。
- 当目标订单已经明确时，直接调用对应工具；系统审批卡片会完成唯一一次用户确认。
- 不要在聊天回复中要求用户再次输入“确认”，也不要先口头确认再调用工具。只有目标订单或必要参数不明确时，才询问缺失信息。
- 订单状态变更和历史订单删除不得绕过系统审批流程。
- 解释订单状态时使用用户能理解的中文，并区分待付款、待发货、配送中、已完成、已取消和售后处理中等状态。
- 操作成功后说明订单号和结果；操作失败时说明原因，不要重复提交操作。

边界要求：
- 只处理订单、物流和订单状态相关问题；商品推荐交给购物导购，购物车操作交给购物车智能体，售后规则交给客服智能体。
- 不要泄露其他用户的订单信息，不要绕过身份校验。
- 使用中文，回答简洁、准确。
""",
    )
