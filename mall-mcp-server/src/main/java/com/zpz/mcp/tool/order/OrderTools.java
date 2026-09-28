package com.zpz.mcp.tool.order;

import com.zpz.mcp.client.Mall4jClientExecutor;
import com.zpz.mcp.client.OrderClient;
import com.zpz.mcp.support.McpAuthorization;
import jakarta.annotation.Resource;
import org.springframework.ai.mcp.annotation.McpTool;
import org.springframework.ai.mcp.annotation.McpToolParam;
import org.springframework.ai.mcp.annotation.context.McpSyncRequestContext;
import org.springframework.stereotype.Component;

/**
 * 将订单和物流 MCP 工具转发到 mall4j 用户订单 REST API。
 */
@Component
public class OrderTools {

    private static final int DEFAULT_PAGE = 1;
    private static final int DEFAULT_SIZE = 10;
    private static final int MAX_SIZE = 20;

    @Resource
    private OrderClient orderClient;

    @Resource
    private Mall4jClientExecutor clientExecutor;

    /**
     * 分页查询当前用户订单。
     *
     * @return mall4j 订单分页响应
     */
    @McpTool(
            name = "order_list",
            title = "查询订单列表",
            description = "分页查询当前登录用户的订单。status取0全部、1待付款、2待发货、3待收货、4待评价、5成功、6失败。",
            annotations = @McpTool.McpAnnotations(
                    title = "查询订单列表",
                    readOnlyHint = true,
                    destructiveHint = false,
                    idempotentHint = true,
                    openWorldHint = false
            )
    )
    public String list(
            McpSyncRequestContext context,
            @McpToolParam(description = "订单状态，默认0表示全部", required = false) Integer status,
            @McpToolParam(description = "页码，默认1", required = false) Integer current,
            @McpToolParam(description = "每页数量，默认10，最大20", required = false) Integer size) {
        String authorization = McpAuthorization.required(context);
        return clientExecutor.execute(
                "order_list",
                () -> orderClient.list(
                        authorization,
                        status == null ? 0 : status,
                        normalizeCurrent(current),
                        normalizeSize(size)
                )
        );
    }

    /**
     * 查询当前用户的订单详情。
     *
     * @param context MCP 请求上下文
     * @param orderNumber 订单号
     * @return mall4j 订单详情响应
     */
    @McpTool(
            name = "order_get_detail",
            title = "查询订单详情",
            description = "根据订单号查询当前登录用户的订单详情、商品、金额、地址和状态。",
            annotations = @McpTool.McpAnnotations(
                    title = "查询订单详情",
                    readOnlyHint = true,
                    destructiveHint = false,
                    idempotentHint = true,
                    openWorldHint = false
            )
    )
    public String getDetail(
            McpSyncRequestContext context,
            @McpToolParam(description = "订单号", required = true) String orderNumber) {
        String authorization = McpAuthorization.required(context);
        return clientExecutor.execute(
                "order_get_detail",
                () -> orderClient.getDetail(authorization, orderNumber)
        );
    }

    /**
     * 查询当前用户各状态订单数量。
     *
     * @param context MCP 请求上下文
     * @return mall4j 订单数量响应
     */
    @McpTool(
            name = "order_get_counts",
            title = "查询订单数量",
            description = "查询当前登录用户各订单状态对应的订单数量。",
            annotations = @McpTool.McpAnnotations(
                    title = "查询订单数量",
                    readOnlyHint = true,
                    destructiveHint = false,
                    idempotentHint = true,
                    openWorldHint = false
            )
    )
    public String getCounts(McpSyncRequestContext context) {
        String authorization = McpAuthorization.required(context);
        return clientExecutor.execute("order_get_counts", () -> orderClient.getCounts(authorization));
    }

    /**
     * 查询当前用户订单物流。
     *
     * <p>调用物流接口前先调用订单详情接口验证订单归属。</p>
     *
     * @param context MCP 请求上下文
     * @param orderNumber 订单号
     * @return mall4j 物流响应
     */
    @McpTool(
            name = "order_get_logistics",
            title = "查询订单物流",
            description = "根据订单号查询当前登录用户订单的物流公司、运单号和物流轨迹。",
            annotations = @McpTool.McpAnnotations(
                    title = "查询订单物流",
                    readOnlyHint = true,
                    destructiveHint = false,
                    idempotentHint = true,
                    openWorldHint = true
            )
    )
    public String getLogistics(
            McpSyncRequestContext context,
            @McpToolParam(description = "订单号", required = true) String orderNumber) {
        String authorization = McpAuthorization.required(context);
        clientExecutor.execute(
                "order_verify_for_logistics",
                () -> orderClient.getDetail(authorization, orderNumber)
        );
        return clientExecutor.execute(
                "order_get_logistics",
                () -> orderClient.getLogistics(authorization, orderNumber)
        );
    }

    /**
     * 取消当前用户的待付款订单。
     *
     * @param context MCP 请求上下文
     * @param orderNumber 订单号
     * @return mall4j 操作响应
     */
    @McpTool(
            name = "order_cancel",
            title = "取消订单",
            description = "取消当前登录用户的待付款订单。调用前必须展示目标订单并取得用户明确确认。",
            annotations = @McpTool.McpAnnotations(
                    title = "取消订单",
                    readOnlyHint = false,
                    destructiveHint = true,
                    idempotentHint = false,
                    openWorldHint = false
            )
    )
    public String cancel(
            McpSyncRequestContext context,
            @McpToolParam(description = "需要取消的订单号", required = true) String orderNumber) {
        String authorization = McpAuthorization.required(context);
        return clientExecutor.execute(
                "order_cancel",
                () -> orderClient.cancel(authorization, orderNumber)
        );
    }

    /**
     * 确认当前用户的订单已收货。
     *
     * @param context MCP 请求上下文
     * @param orderNumber 订单号
     * @return mall4j 操作响应
     */
    @McpTool(
            name = "order_confirm_receipt",
            title = "确认收货",
            description = "确认当前登录用户的已发货订单已经收货。调用前必须展示目标订单并取得用户明确确认。",
            annotations = @McpTool.McpAnnotations(
                    title = "确认收货",
                    readOnlyHint = false,
                    destructiveHint = true,
                    idempotentHint = false,
                    openWorldHint = false
            )
    )
    public String confirmReceipt(
            McpSyncRequestContext context,
            @McpToolParam(description = "需要确认收货的订单号", required = true) String orderNumber) {
        String authorization = McpAuthorization.required(context);
        return clientExecutor.execute(
                "order_confirm_receipt",
                () -> orderClient.confirmReceipt(authorization, orderNumber)
        );
    }

    /**
     * 删除已完成或已关闭的历史订单。
     *
     * @param context MCP 请求上下文
     * @param orderNumber 订单号
     * @return mall4j 操作响应
     */
    @McpTool(
            name = "order_delete_history",
            title = "删除历史订单",
            description = "删除当前登录用户已完成或已关闭的历史订单。该操作不可逆，调用前必须取得明确确认。",
            annotations = @McpTool.McpAnnotations(
                    title = "删除历史订单",
                    readOnlyHint = false,
                    destructiveHint = true,
                    idempotentHint = true,
                    openWorldHint = false
            )
    )
    public String deleteHistory(
            McpSyncRequestContext context,
            @McpToolParam(description = "需要删除的历史订单号", required = true) String orderNumber) {
        String authorization = McpAuthorization.required(context);
        return clientExecutor.execute(
                "order_delete_history",
                () -> orderClient.deleteHistory(authorization, orderNumber)
        );
    }

    private int normalizeCurrent(Integer current) {
        return current == null ? DEFAULT_PAGE : Math.max(1, current);
    }

    private int normalizeSize(Integer size) {
        return size == null ? DEFAULT_SIZE : Math.max(1, Math.min(size, MAX_SIZE));
    }
}
