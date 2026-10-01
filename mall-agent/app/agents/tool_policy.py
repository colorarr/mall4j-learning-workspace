from dataclasses import dataclass
from enum import StrEnum
from typing import Mapping


class ToolRisk(StrEnum):
    """ 工具操作风险的枚举类 """

    #只读
    READ_ONLY = "read_only"

    #写
    WRITE = "write"

    #危险写操作
    DANGEROUS_WRITE = "dangerous_write"


@dataclass(frozen=True, slots=True)
class ToolPolicy:
    """单个工具的执行策略。"""

    risk: ToolRisk
    retryable: bool = False
    requires_approval: bool = False


CART_TOOL_POLICIES: dict[str, ToolPolicy] = {
    # 查询操作：允许对临时网络异常进行重试
    "cart_get": ToolPolicy(
        risk=ToolRisk.READ_ONLY,
        retryable=True,
    ),
    "cart_get_count": ToolPolicy(
        risk=ToolRisk.READ_ONLY,
        retryable=True,
    ),
    "cart_get_total": ToolPolicy(
        risk=ToolRisk.READ_ONLY,
        retryable=True,
    ),
    "cart_get_expired_items": ToolPolicy(
        risk=ToolRisk.READ_ONLY,
        retryable=True,
    ),

    # 普通写操作：可能产生重复变更，因此暂不自动重试
    "cart_add_item": ToolPolicy(
        risk=ToolRisk.WRITE,
    ),
    "cart_change_quantity": ToolPolicy(
        risk=ToolRisk.WRITE,
    ),

    # 危险写操作：执行前需要用户确认
    "cart_remove_items": ToolPolicy(
        risk=ToolRisk.DANGEROUS_WRITE,
        requires_approval=True,
    ),
    "cart_clear": ToolPolicy(
        risk=ToolRisk.DANGEROUS_WRITE,
        requires_approval=True,
    ),
    "cart_clean_expired_items": ToolPolicy(
        risk=ToolRisk.DANGEROUS_WRITE,
        requires_approval=True,
    ),
}


ORDER_TOOL_POLICIES: dict[str, ToolPolicy] = {
    # 订单与物流查询：只读且允许对临时故障进行重试
    "order_list": ToolPolicy(
        risk=ToolRisk.READ_ONLY,
        retryable=True,
    ),
    "order_get_detail": ToolPolicy(
        risk=ToolRisk.READ_ONLY,
        retryable=True,
    ),
    "order_get_counts": ToolPolicy(
        risk=ToolRisk.READ_ONLY,
        retryable=True,
    ),
    "order_get_logistics": ToolPolicy(
        risk=ToolRisk.READ_ONLY,
        retryable=True,
    ),

    # 订单状态变更：不自动重试，执行前必须由用户审批
    "order_cancel": ToolPolicy(
        risk=ToolRisk.DANGEROUS_WRITE,
        requires_approval=True,
    ),
    "order_confirm_receipt": ToolPolicy(
        risk=ToolRisk.DANGEROUS_WRITE,
        requires_approval=True,
    ),
    "order_delete_history": ToolPolicy(
        risk=ToolRisk.DANGEROUS_WRITE,
        requires_approval=True,
    ),
}


SHOPPING_TOOL_POLICIES: dict[str, ToolPolicy] = {
    # 商品工具全部为只读查询，可以对临时故障进行重试
    "product_search": ToolPolicy(
        risk=ToolRisk.READ_ONLY,
        retryable=True,
    ),
    "product_get_detail": ToolPolicy(
        risk=ToolRisk.READ_ONLY,
        retryable=True,
    ),
    "product_get_skus": ToolPolicy(
        risk=ToolRisk.READ_ONLY,
        retryable=True,
    ),
    "product_get_newest": ToolPolicy(
        risk=ToolRisk.READ_ONLY,
        retryable=True,
    ),
    "product_get_best_sellers": ToolPolicy(
        risk=ToolRisk.READ_ONLY,
        retryable=True,
    ),
    "product_get_review_summary": ToolPolicy(
        risk=ToolRisk.READ_ONLY,
        retryable=True,
    ),
    "product_get_reviews": ToolPolicy(
        risk=ToolRisk.READ_ONLY,
        retryable=True,
    ),
    "product_get_hot_searches": ToolPolicy(
        risk=ToolRisk.READ_ONLY,
        retryable=True,
    ),
}


CUSTOMER_TOOL_POLICIES: dict[str, ToolPolicy] = {
    # 公告与地址查询：只读且允许重试
    "customer_get_top_notices": ToolPolicy(
        risk=ToolRisk.READ_ONLY,
        retryable=True,
    ),
    "customer_list_notices": ToolPolicy(
        risk=ToolRisk.READ_ONLY,
        retryable=True,
    ),
    "customer_get_notice_detail": ToolPolicy(
        risk=ToolRisk.READ_ONLY,
        retryable=True,
    ),
    "address_list": ToolPolicy(
        risk=ToolRisk.READ_ONLY,
        retryable=True,
    ),
    "address_get_detail": ToolPolicy(
        risk=ToolRisk.READ_ONLY,
        retryable=True,
    ),

    # 地址写操作不自动重试，其中不可逆的删除操作需要审批
    "address_add": ToolPolicy(
        risk=ToolRisk.WRITE,
    ),
    "address_update": ToolPolicy(
        risk=ToolRisk.WRITE,
    ),
    "address_set_default": ToolPolicy(
        risk=ToolRisk.WRITE,
    ),
    "address_delete": ToolPolicy(
        risk=ToolRisk.DANGEROUS_WRITE,
        requires_approval=True,
    ),
}


def get_retryable_tool_names(policies:Mapping[str, ToolPolicy]) -> list[str]:
    """ 获取允许重试的工具名字 """
    retryable_tool_names: list[str] = []

    for tool_name, policy in policies.items():
        if policy.retryable:
            retryable_tool_names.append(tool_name)

    return retryable_tool_names


def get_approval_tool_names(
        policies:Mapping[str, ToolPolicy]
)->list[str]:
    """ 返回需要人工授权的工具名字 """
    approval_tool_names: list[str] = []

    for tool_name, policy in policies.items():
        if policy.requires_approval:
            approval_tool_names.append(tool_name)

    return approval_tool_names
