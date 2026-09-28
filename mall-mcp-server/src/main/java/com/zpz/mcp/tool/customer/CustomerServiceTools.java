package com.zpz.mcp.tool.customer;

import com.zpz.mcp.client.CustomerServiceClient;
import com.zpz.mcp.client.Mall4jClientExecutor;
import jakarta.annotation.Resource;
import org.springframework.ai.mcp.annotation.McpTool;
import org.springframework.ai.mcp.annotation.McpToolParam;
import org.springframework.stereotype.Component;

/**
 * 将商城公告类客服工具转发到 mall4j 公告 REST API。
 */
@Component
public class CustomerServiceTools {

    private static final int DEFAULT_PAGE = 1;
    private static final int DEFAULT_SIZE = 10;
    private static final int MAX_SIZE = 20;

    @Resource
    private CustomerServiceClient customerServiceClient;

    @Resource
    private Mall4jClientExecutor clientExecutor;

    /**
     * 查询商城置顶公告。
     */
    @McpTool(
            name = "customer_get_top_notices",
            title = "查询置顶公告",
            description = "查询商城当前置顶公告，可用于回答平台活动和重要通知问题。",
            annotations = @McpTool.McpAnnotations(
                    title = "查询置顶公告",
                    readOnlyHint = true,
                    destructiveHint = false,
                    idempotentHint = true,
                    openWorldHint = false
            )
    )
    public String getTopNotices() {
        return clientExecutor.execute("customer_get_top_notices", customerServiceClient::getTopNotices);
    }

    /**
     * 分页查询商城公告。
     */
    @McpTool(
            name = "customer_list_notices",
            title = "查询商城公告",
            description = "分页查询商城公告列表。先获取列表，再根据公告ID查询具体内容。",
            annotations = @McpTool.McpAnnotations(
                    title = "查询商城公告",
                    readOnlyHint = true,
                    destructiveHint = false,
                    idempotentHint = true,
                    openWorldHint = false
            )
    )
    public String listNotices(
            @McpToolParam(description = "页码，默认1", required = false) Integer current,
            @McpToolParam(description = "每页数量，默认10，最大20", required = false) Integer size) {
        int actualCurrent = current == null ? DEFAULT_PAGE : Math.max(1, current);
        int actualSize = size == null ? DEFAULT_SIZE : Math.max(1, Math.min(size, MAX_SIZE));
        return clientExecutor.execute(
                "customer_list_notices",
                () -> customerServiceClient.listNotices(actualCurrent, actualSize)
        );
    }

    /**
     * 查询商城公告详情。
     */
    @McpTool(
            name = "customer_get_notice_detail",
            title = "查询公告详情",
            description = "根据公告ID查询商城公告的完整内容。",
            annotations = @McpTool.McpAnnotations(
                    title = "查询公告详情",
                    readOnlyHint = true,
                    destructiveHint = false,
                    idempotentHint = true,
                    openWorldHint = false
            )
    )
    public String getNoticeDetail(
            @McpToolParam(description = "公告ID", required = true) Long noticeId) {
        return clientExecutor.execute(
                "customer_get_notice_detail",
                () -> customerServiceClient.getNoticeDetail(noticeId)
        );
    }
}
