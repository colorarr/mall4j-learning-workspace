package com.zpz.mcp.support;

import org.springframework.ai.mcp.annotation.context.McpSyncRequestContext;
import org.springframework.http.HttpHeaders;
import org.springframework.util.StringUtils;

/**
 * 从 MCP 请求上下文读取商城用户认证信息。
 */
public final class McpAuthorization {

    private McpAuthorization() {
    }

    /**
     * 获取可选的 Authorization 请求头。
     *
     * @param context MCP 同步请求上下文
     * @return Authorization；请求未携带时返回 null
     */
    public static String optional(McpSyncRequestContext context) {
        Object authorization = context.transportContext().get(HttpHeaders.AUTHORIZATION);
        return authorization instanceof String value && StringUtils.hasText(value) ? value : null;
    }

    /**
     * 获取受保护工具必需的 Authorization 请求头。
     *
     * @param context MCP 同步请求上下文
     * @return Authorization
     * @throws IllegalStateException 请求未携带 Authorization 时抛出
     */
    public static String required(McpSyncRequestContext context) {
        String authorization = optional(context);
        if (!StringUtils.hasText(authorization)) {
            throw new IllegalStateException("该工具需要用户登录，请在 MCP 请求中携带 Authorization");
        }
        return authorization;
    }
}
