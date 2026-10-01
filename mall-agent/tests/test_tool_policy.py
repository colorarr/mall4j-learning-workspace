import unittest

from app.agents.tool_policy import (
    CART_TOOL_POLICIES,
    CUSTOMER_TOOL_POLICIES,
    ORDER_TOOL_POLICIES,
    SHOPPING_TOOL_POLICIES,
    ToolRisk,
    get_approval_tool_names,
    get_retryable_tool_names,
)


class TestCartToolPolicy(unittest.TestCase):

    def test_retryable_tools(self):
        tool_names = get_retryable_tool_names(CART_TOOL_POLICIES)

        self.assertEqual(
            set(tool_names),
            {
                "cart_get",
                "cart_get_count",
                "cart_get_total",
                "cart_get_expired_items",
            },
        )

    def test_approval_tools(self):
        tool_names = get_approval_tool_names(CART_TOOL_POLICIES)

        self.assertEqual(
            set(tool_names),
            {
                "cart_remove_items",
                "cart_clear",
                "cart_clean_expired_items",
            },
        )

    def test_retryable_tools_are_read_only(self):
        for tool_name in get_retryable_tool_names(CART_TOOL_POLICIES):
            with self.subTest(tool_name=tool_name):
                policy = CART_TOOL_POLICIES[tool_name]
                self.assertEqual(policy.risk, ToolRisk.READ_ONLY)

    def test_dangerous_tools_require_approval(self):
        for tool_name, policy in CART_TOOL_POLICIES.items():
            with self.subTest(tool_name=tool_name):
                if policy.risk == ToolRisk.DANGEROUS_WRITE:
                    self.assertTrue(policy.requires_approval)


class TestOrderToolPolicy(unittest.TestCase):

    def test_retryable_tools(self):
        tool_names = get_retryable_tool_names(ORDER_TOOL_POLICIES)

        self.assertEqual(
            set(tool_names),
            {
                "order_list",
                "order_get_detail",
                "order_get_counts",
                "order_get_logistics",
            },
        )

    def test_approval_tools(self):
        tool_names = get_approval_tool_names(ORDER_TOOL_POLICIES)

        self.assertEqual(
            set(tool_names),
            {
                "order_cancel",
                "order_confirm_receipt",
                "order_delete_history",
            },
        )


class TestShoppingToolPolicy(unittest.TestCase):

    def test_all_shopping_tools_are_retryable_read_only(self):
        retryable_tools = set(
            get_retryable_tool_names(SHOPPING_TOOL_POLICIES)
        )

        self.assertEqual(
            retryable_tools,
            set(SHOPPING_TOOL_POLICIES),
        )
        self.assertEqual(
            get_approval_tool_names(SHOPPING_TOOL_POLICIES),
            [],
        )

        for tool_name, policy in SHOPPING_TOOL_POLICIES.items():
            with self.subTest(tool_name=tool_name):
                self.assertEqual(policy.risk, ToolRisk.READ_ONLY)


class TestCustomerToolPolicy(unittest.TestCase):

    def test_retryable_tools(self):
        tool_names = get_retryable_tool_names(CUSTOMER_TOOL_POLICIES)

        self.assertEqual(
            set(tool_names),
            {
                "customer_get_top_notices",
                "customer_list_notices",
                "customer_get_notice_detail",
                "address_list",
                "address_get_detail",
            },
        )

    def test_approval_tools(self):
        tool_names = get_approval_tool_names(CUSTOMER_TOOL_POLICIES)

        self.assertEqual(
            set(tool_names),
            {
                "address_delete",
            },
        )


class TestAllToolPolicies(unittest.TestCase):

    def test_retryable_tools_are_read_only(self):
        all_policies = (
            CART_TOOL_POLICIES,
            ORDER_TOOL_POLICIES,
            SHOPPING_TOOL_POLICIES,
            CUSTOMER_TOOL_POLICIES,
        )

        for policies in all_policies:
            for tool_name in get_retryable_tool_names(policies):
                with self.subTest(tool_name=tool_name):
                    self.assertEqual(
                        policies[tool_name].risk,
                        ToolRisk.READ_ONLY,
                    )

    def test_approval_tools_are_not_retryable(self):
        all_policies = (
            CART_TOOL_POLICIES,
            ORDER_TOOL_POLICIES,
            SHOPPING_TOOL_POLICIES,
            CUSTOMER_TOOL_POLICIES,
        )

        for policies in all_policies:
            approval_tools = set(get_approval_tool_names(policies))
            retryable_tools = set(get_retryable_tool_names(policies))
            self.assertTrue(approval_tools.isdisjoint(retryable_tools))

    def test_dangerous_tools_require_approval(self):
        all_policies = (
            CART_TOOL_POLICIES,
            ORDER_TOOL_POLICIES,
            SHOPPING_TOOL_POLICIES,
            CUSTOMER_TOOL_POLICIES,
        )

        for policies in all_policies:
            for tool_name, policy in policies.items():
                with self.subTest(tool_name=tool_name):
                    if policy.risk == ToolRisk.DANGEROUS_WRITE:
                        self.assertTrue(policy.requires_approval)


if __name__ == "__main__":
    unittest.main()
