from enum import Enum

from pydantic import BaseModel, Field


class IntentType(str, Enum):
    """商城智能体可识别的用户意图类型。"""

    # 商品推荐：根据用途、预算或偏好推荐商品
    PRODUCT_RECOMMENDATION = "product_recommendation"
    # 商品搜索：按照关键词或筛选条件查找商品
    PRODUCT_SEARCH = "product_search"
    # 商品详情：查询商品的规格、价格、库存等信息
    PRODUCT_DETAIL = "product_detail"
    # 商品对比：比较两个或多个商品的差异
    PRODUCT_COMPARE = "product_compare"
    # 查询购物车：查看购物车内容和金额
    CART_QUERY = "cart_query"
    # 添加购物车：将商品加入购物车
    CART_ADD = "cart_add"
    # 修改购物车：修改商品数量或规格
    CART_UPDATE = "cart_update"
    # 删除购物车：删除商品或清空购物车
    CART_REMOVE = "cart_remove"
    # 查询订单：查看订单列表、详情或订单状态
    ORDER_QUERY = "order_query"
    # 查询物流：查看配送和物流轨迹
    ORDER_LOGISTICS = "order_logistics"
    # 取消订单：申请取消尚未完成的订单
    ORDER_CANCEL = "order_cancel"
    # 售后服务：咨询或办理退款、退货、换货等售后事项
    AFTER_SALE = "after_sale"
    # 客服咨询：咨询配送、支付、优惠和平台规则等问题
    CUSTOMER_SERVICE = "customer_service"
    # 人工转接：用户要求人工或问题需要人工处理
    HUMAN_TRANSFER = "human_transfer"
    # 未知意图：无法判断或不属于商城服务范围
    UNKNOWN = "unknown"


class IntentResult(BaseModel):
    intent: IntentType = Field(
        description="用户当前最主要的意图，只能选择定义好的意图类型",
    )
    intent_reason: str = Field(
        min_length=1,
        description="用一句话说明判断该意图的依据",
    )
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="意图识别置信度，取值范围为 0 到 1",
    )
