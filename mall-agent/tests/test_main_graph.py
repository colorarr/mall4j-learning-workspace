import os
import unittest

from langgraph.checkpoint.memory import InMemorySaver

from app.auth.request_context import reset_authorization, set_authorization
from app.graph.main_graph import build_graph
from app.graph.state import AgentState
from app.schemas.intent import IntentType


class TestMainGraphIntegration(unittest.IsolatedAsyncioTestCase):
    """使用真实模型配置验证主 Graph 的意图识别和条件路由。"""

    @classmethod
    def setUpClass(cls):
        cls.graph = build_graph(InMemorySaver())

    async def test_routes_business_requests(self):
        authorization = os.getenv("MALL_TEST_TOKEN")
        if not authorization:
            self.skipTest("未配置 MALL_TEST_TOKEN，跳过真实商城集成测试")

        context_token = set_authorization(authorization)
        cases = [
            (
                "推荐一个适合通勤的双肩包",
                IntentType.PRODUCT_RECOMMENDATION,
                "shopping",
            ),
            (
                "查看我的购物车",
                IntentType.CART_QUERY,
                "cart",
            ),
            (
                "查询我的订单物流",
                IntentType.ORDER_LOGISTICS,
                "order",
            ),
            (
                "我想咨询退货规则",
                IntentType.AFTER_SALE,
                "customer",
            ),
        ]

        try:
            for user_input, expected_intent, expected_agent in cases:
                with self.subTest(user_input=user_input):
                    result = await self.graph.ainvoke(
                        AgentState(user_input=user_input).model_dump(),
                        config={
                            "configurable": {
                                "thread_id": (
                                    f"test-main-graph-{expected_agent}"
                                ),
                            }
                        },
                    )

                    self.assertEqual(result["intent"], expected_intent)
                    self.assertIsInstance(result["confidence"], float)
                    self.assertEqual(result["current_agent"], expected_agent)
                    self.assertTrue(result["messages"])
                    self.assertTrue(result["messages"][-1].content)
        finally:
            reset_authorization(context_token)


if __name__ == "__main__":
    unittest.main()
