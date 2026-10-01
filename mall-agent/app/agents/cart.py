from langchain.agents import create_agent
from langchain.agents.middleware import ToolRetryMiddleware, ModelRetryMiddleware, ModelCallLimitMiddleware, \
    ToolCallLimitMiddleware, HumanInTheLoopMiddleware

from app.agents.tool_policy import get_retryable_tool_names, CART_TOOL_POLICIES, get_approval_tool_names
from app.core.llm import get_glm_model
from app.mcp.client import load_current_user_tools


async def get_cart_agent():
    """创建携带当前用户购物车和商品工具的智能体。"""
    cart_tools = await load_current_user_tools(
        "cart_",
        "product_",
    )

    #获取可重试工具名单
    retryable_tool_names = get_retryable_tool_names(CART_TOOL_POLICIES)

    #获取需要人工介入的工具名称
    approval_tool_names = get_approval_tool_names(CART_TOOL_POLICIES)

    approval_descriptions = {
        "cart_remove_items": "将删除选中的购物车商品，批准后立即执行。",
        "cart_clear": "将清空购物车中的全部商品，批准后立即执行。",
        "cart_clean_expired_items": "将删除购物车中的全部失效商品，批准后立即执行。",
    }

    #定义人工介入中间件
    human_in_the_loop_middleware = HumanInTheLoopMiddleware(
        interrupt_on={
            tool_name: {
                "allowed_decisions": [
                    "approve",
                    "reject",
                ],
                "description": approval_descriptions.get(
                    tool_name,
                    "该操作会修改购物车数据，批准后立即执行。",
                ),
            }
            for tool_name in approval_tool_names
        },
        description_prefix="购物车操作需要用户确认",
    )
    #定义模型调用次数的中间件
    model_call_limit = ModelCallLimitMiddleware(
        run_limit=8,
        exit_behavior="end",
    )

    #定义工具调用次数的中间件
    tool_call_limit = ToolCallLimitMiddleware(run_limit=12, exit_behavior="end", )

    #定义工具重试的中间件
    tool_retry_middleware = ToolRetryMiddleware(tools=retryable_tool_names, max_retries=2, initial_delay=1.0, backoff_factor=2.0,
                                     max_delay=8.0, jitter=True, on_failure="continue", )

    #定义模型重试的中间件
    model_retry_middleware = ModelRetryMiddleware(max_retries=2, initial_delay=1.0, backoff_factor=2.0, max_delay=8.0, jitter=True,
                                      on_failure="error", )

    return create_agent(
        name="cart_agent",
        model=get_glm_model(),
        tools=cart_tools,
        middleware=[
            model_call_limit,
            tool_call_limit,
            model_retry_middleware,
            tool_retry_middleware,
            human_in_the_loop_middleware,
        ],
        system_prompt="""
你是商城购物车智能体，负责处理用户的购物车查询和编辑请求。

工作要求：
- 准确识别用户要查看购物车、添加商品、修改数量、删除商品还是清空购物车。
- 涉及商品时，先确认商品 ID、规格、数量等必要信息；信息不足时只提出一到两个简短问题。
- 需要购物车或商品数据时，必须调用对应工具；没有工具结果时，不得编造商品、规格、数量、价格或库存。
- 添加商品前确认商品规格和购买数量。
- 当用户明确要求删除、清空或清理购物车，且操作目标已经明确时，直接调用对应工具；系统审批窗口会完成唯一一次用户确认。
- 不要在聊天回复中要求用户再次输入“确认”，也不要先进行口头确认再调用工具。只有操作目标或必要参数不明确时，才询问缺失信息。
- 删除、清空购物车和清理失效商品等操作不得绕过系统审批流程。
- 操作成功后说明实际变更结果；操作失败时说明原因，并给出下一步建议。

边界要求：
- 只处理购物车相关操作，不负责商品推荐、订单查询、支付或售后问题。
- 不要擅自提交订单或发起支付。
- 使用中文，回答简洁、清楚地列出商品名称、规格和数量。
""",
    )
