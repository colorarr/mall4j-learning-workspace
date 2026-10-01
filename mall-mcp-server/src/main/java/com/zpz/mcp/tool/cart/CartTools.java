package com.zpz.mcp.tool.cart;

import com.zpz.mcp.client.CartClient;
import com.zpz.mcp.client.Mall4jClientExecutor;
import com.zpz.mcp.support.McpAuthorization;
import jakarta.annotation.Resource;
import org.springframework.ai.mcp.annotation.McpTool;
import org.springframework.ai.mcp.annotation.McpToolParam;
import org.springframework.ai.mcp.annotation.context.McpSyncRequestContext;
import org.springframework.stereotype.Component;

import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * 将购物车 MCP 工具转发到 mall4j 购物车 REST API。
 */
@Component
public class CartTools {

    @Resource
    private CartClient cartClient;

    @Resource
    private Mall4jClientExecutor clientExecutor;

    /**
     * 查询当前登录用户的购物车。
     *
     * @param context MCP 请求上下文
     * @return mall4j 购物车响应
     */
    @McpTool(
            name = "cart_get",
            title = "查询购物车",
            description = "查询当前登录用户的购物车，返回商品、SKU、数量、价格、优惠和店铺分组信息。",
            annotations = @McpTool.McpAnnotations(
                    title = "查询购物车",
                    readOnlyHint = true,
                    destructiveHint = false,
                    idempotentHint = true,
                    openWorldHint = false
            )
    )
    public String getCart(McpSyncRequestContext context) {
        String authorization = McpAuthorization.required(context);
        return clientExecutor.execute("cart_get", () -> cartClient.getCart(authorization, Map.of()));
    }

    /**
     * 将指定商品加入当前用户购物车。
     *
     * @param context MCP 请求上下文
     * @param request 加购参数
     * @return mall4j 操作响应
     */
    @McpTool(
            name = "cart_add_item",
            title = "加入购物车",
            description = "把指定商品SKU加入当前用户购物车。changeCount必须是大于0的购买数量。",
            annotations = @McpTool.McpAnnotations(
                    title = "加入购物车",
                    readOnlyHint = false,
                    destructiveHint = false,
                    idempotentHint = false,
                    openWorldHint = false
            )
    )
    public String addItem(
            McpSyncRequestContext context,
            @McpToolParam(description = "商品、SKU、店铺和增加数量", required = true)
            CartChangeRequest request) {
        if (request.changeCount() == null || request.changeCount() <= 0) {
            throw new IllegalArgumentException("加入购物车的 changeCount 必须大于 0");
        }
        String authorization = McpAuthorization.required(context);
        return clientExecutor.execute(
                "cart_add_item",
                () -> cartClient.changeItem(authorization, toMall4jRequest(request))
        );
    }

    /**
     * 增加或减少购物车商品数量。
     *
     * @param context MCP 请求上下文
     * @param request 数量变化参数
     * @return mall4j 操作响应
     */
    @McpTool(
            name = "cart_change_quantity",
            title = "调整购物车数量",
            description = "按变化值调整购物车商品数量。changeCount为正数时增加，为负数时减少，不能为0。",
            annotations = @McpTool.McpAnnotations(
                    title = "调整购物车数量",
                    readOnlyHint = false,
                    destructiveHint = false,
                    idempotentHint = false,
                    openWorldHint = false
            )
    )
    public String changeQuantity(
            McpSyncRequestContext context,
            @McpToolParam(description = "商品、SKU、店铺和数量变化值", required = true)
            CartChangeRequest request) {
        if (request.changeCount() == null || request.changeCount() == 0) {
            throw new IllegalArgumentException("changeCount 不能为 0");
        }
        String authorization = McpAuthorization.required(context);
        return clientExecutor.execute(
                "cart_change_quantity",
                () -> cartClient.changeItem(authorization, toMall4jRequest(request))
        );
    }

    /**
     * 删除购物车中的指定明细。
     *
     * @param context MCP 请求上下文
     * @param basketIds 购物车明细 ID 列表
     * @return mall4j 操作响应
     */
    @McpTool(
            name = "cart_remove_items",
            title = "删除购物车商品",
            description = "根据购物车明细ID列表删除当前用户购物车中的商品。目标明确后直接调用，系统会在执行前通过审批界面确认。",
            annotations = @McpTool.McpAnnotations(
                    title = "删除购物车商品",
                    readOnlyHint = false,
                    destructiveHint = true,
                    idempotentHint = true,
                    openWorldHint = false
            )
    )
    public String removeItems(
            McpSyncRequestContext context,
            @McpToolParam(description = "需要删除的购物车明细ID列表", required = true)
            List<Long> basketIds) {
        String authorization = McpAuthorization.required(context);
        return clientExecutor.execute(
                "cart_remove_items",
                () -> cartClient.removeItems(authorization, basketIds)
        );
    }

    /**
     * 清空当前用户购物车。
     *
     * @param context MCP 请求上下文
     * @return mall4j 操作响应
     */
    @McpTool(
            name = "cart_clear",
            title = "清空购物车",
            description = "清空当前登录用户的全部购物车商品。目标明确后直接调用，系统会在执行前通过审批界面确认。",
            annotations = @McpTool.McpAnnotations(
                    title = "清空购物车",
                    readOnlyHint = false,
                    destructiveHint = true,
                    idempotentHint = true,
                    openWorldHint = false
            )
    )
    public String clear(McpSyncRequestContext context) {
        String authorization = McpAuthorization.required(context);
        return clientExecutor.execute("cart_clear", () -> cartClient.clear(authorization));
    }

    /**
     * 查询购物车商品总数量。
     *
     * @param context MCP 请求上下文
     * @return mall4j 数量响应
     */
    @McpTool(
            name = "cart_get_count",
            title = "查询购物车商品数量",
            description = "查询当前登录用户购物车中的商品总数量。",
            annotations = @McpTool.McpAnnotations(
                    title = "查询购物车商品数量",
                    readOnlyHint = true,
                    destructiveHint = false,
                    idempotentHint = true,
                    openWorldHint = false
            )
    )
    public String getCount(McpSyncRequestContext context) {
        String authorization = McpAuthorization.required(context);
        return clientExecutor.execute("cart_get_count", () -> cartClient.getCount(authorization));
    }

    /**
     * 计算选中购物项的金额汇总。
     *
     * @param context MCP 请求上下文
     * @param basketIds 需要结算的购物车明细 ID
     * @return mall4j 金额响应
     */
    @McpTool(
            name = "cart_get_total",
            title = "计算购物车金额",
            description = "根据购物车明细ID计算选中商品数量、总金额、优惠金额和最终金额。",
            annotations = @McpTool.McpAnnotations(
                    title = "计算购物车金额",
                    readOnlyHint = true,
                    destructiveHint = false,
                    idempotentHint = true,
                    openWorldHint = false
            )
    )
    public String getTotal(
            McpSyncRequestContext context,
            @McpToolParam(description = "参与金额计算的购物车明细ID列表", required = true)
            List<Long> basketIds) {
        String authorization = McpAuthorization.required(context);
        return clientExecutor.execute(
                "cart_get_total",
                () -> cartClient.getTotal(authorization, basketIds)
        );
    }

    /**
     * 查询当前购物车中的失效商品。
     *
     * @param context MCP 请求上下文
     * @return mall4j 失效商品响应
     */
    @McpTool(
            name = "cart_get_expired_items",
            title = "查询失效购物项",
            description = "查询当前登录用户购物车中已经失效或下架的商品。",
            annotations = @McpTool.McpAnnotations(
                    title = "查询失效购物项",
                    readOnlyHint = true,
                    destructiveHint = false,
                    idempotentHint = true,
                    openWorldHint = false
            )
    )
    public String getExpiredItems(McpSyncRequestContext context) {
        String authorization = McpAuthorization.required(context);
        return clientExecutor.execute(
                "cart_get_expired_items",
                () -> cartClient.getExpiredItems(authorization)
        );
    }

    /**
     * 删除购物车中的全部失效商品。
     *
     * @param context MCP 请求上下文
     * @return mall4j 操作响应
     */
    @McpTool(
            name = "cart_clean_expired_items",
            title = "清理失效购物项",
            description = "删除当前用户购物车中的全部失效商品。目标明确后直接调用，系统会在执行前通过审批界面确认。",
            annotations = @McpTool.McpAnnotations(
                    title = "清理失效购物项",
                    readOnlyHint = false,
                    destructiveHint = true,
                    idempotentHint = true,
                    openWorldHint = false
            )
    )
    public String cleanExpiredItems(McpSyncRequestContext context) {
        String authorization = McpAuthorization.required(context);
        return clientExecutor.execute(
                "cart_clean_expired_items",
                () -> cartClient.cleanExpiredItems(authorization)
        );
    }

    private Map<String, Object> toMall4jRequest(CartChangeRequest request) {
        Map<String, Object> body = new LinkedHashMap<>();
        body.put("basketId", request.basketId());
        body.put("prodId", request.productId());
        body.put("skuId", request.skuId());
        body.put("shopId", request.shopId());
        body.put("count", request.changeCount());
        body.put("distributionCardNo", request.distributionCardNo());
        return body;
    }
}
