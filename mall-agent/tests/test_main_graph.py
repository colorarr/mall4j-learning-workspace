import unittest

from app.graph.main_graph import build_graph
from app.graph.state import AgentState
from app.schemas.intent import IntentType


class TestMainGraphIntegration(unittest.TestCase):
    """使用真实模型配置验证主 Graph 的意图识别和条件路由。"""

    @classmethod
    def setUpClass(cls):
        cls.graph = build_graph(AgentState)

    def test_routes_business_requests(self):
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

        for user_input, expected_intent, expected_agent in cases:
            with self.subTest(user_input=user_input):
                result = self.graph.invoke(
                    AgentState(user_input=user_input).model_dump()
                )

                self.assertEqual(result["intent"], expected_intent)
                self.assertIsInstance(result["confidence"], float)
                self.assertEqual(result["current_agent"], expected_agent)
                self.assertTrue(result["messages"])
                self.assertTrue(result["messages"][-1].content)


if __name__ == "__main__":
    unittest.main()
