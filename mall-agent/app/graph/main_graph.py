from langgraph.graph import END, START, StateGraph

from app.graph.nodes.cart_node import cart_node
from app.graph.nodes.customer_service_node import customer_service_node
from app.graph.nodes.order_node import order_node
from app.graph.nodes.router_node import intent_node
from app.graph.nodes.shopping_node import shopping_node
from app.schemas.intent import IntentType
from app.graph.state import AgentState


shopping_type = [
    IntentType.PRODUCT_RECOMMENDATION,
    IntentType.PRODUCT_SEARCH,
    IntentType.PRODUCT_DETAIL,
    IntentType.PRODUCT_COMPARE,
]

cart_type = [
    IntentType.CART_QUERY,
    IntentType.CART_ADD,
    IntentType.CART_UPDATE,
    IntentType.CART_REMOVE,
]

customer_type = [
    IntentType.AFTER_SALE,
    IntentType.CUSTOMER_SERVICE,
    IntentType.HUMAN_TRANSFER,
    IntentType.UNKNOWN,
]

order_type = [
    IntentType.ORDER_QUERY,
    IntentType.ORDER_LOGISTICS,
    IntentType.ORDER_CANCEL,
]

def route_by_intent(state: AgentState) -> str:
    """根据意图枚举返回下一个业务节点名称。"""
    if state.intent in shopping_type:
        return "shopping"
    if state.intent in cart_type:
        return "cart"
    if state.intent in customer_type:
        return "customer"
    if state.intent in order_type:
        return "order"
    return "customer"


def build_graph(state: AgentState):
    graph = StateGraph(state)


    #添加节点
    graph.add_node("intent", intent_node)
    graph.add_node("customer", customer_service_node)
    graph.add_node("shopping", shopping_node)
    graph.add_node("cart", cart_node)
    graph.add_node("order", order_node)

    #定义边
    graph.add_edge(START, "intent")
    graph.add_conditional_edges(
        "intent",
        route_by_intent,
        {
            "shopping": "shopping",
            "cart": "cart",
            "customer": "customer",
            "order":"order",
        },
    )
    graph.add_edge("shopping", END)
    graph.add_edge("cart", END)
    graph.add_edge("customer", END)
    graph.add_edge("order", END)

    return graph.compile()
