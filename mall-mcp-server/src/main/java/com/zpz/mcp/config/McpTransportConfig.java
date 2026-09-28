package com.zpz.mcp.config;

import io.modelcontextprotocol.common.McpTransportContext;
import io.modelcontextprotocol.json.jackson3.JacksonMcpJsonMapper;
import org.springframework.ai.mcp.server.common.autoconfigure.properties.McpServerStreamableHttpProperties;
import org.springframework.ai.mcp.server.webmvc.transport.WebMvcStreamableServerTransportProvider;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpHeaders;
import org.springframework.util.StringUtils;
import tools.jackson.databind.json.JsonMapper;

import java.util.Map;

/**
 * MCP Streamable HTTP 传输配置，用于把 HTTP 请求头放入工具调用上下文。
 */
@Configuration
public class McpTransportConfig {

    /**
     * 创建携带 Authorization 上下文的 MCP WebMVC 传输提供器。
     *
     * @param jsonMapper MCP 使用的 JSON 映射器
     * @param properties Streamable HTTP 配置
     * @return MCP WebMVC 传输提供器
     */
    @Bean
    public WebMvcStreamableServerTransportProvider webMvcStreamableServerTransportProvider(
            @Qualifier("mcpServerJsonMapper") JsonMapper jsonMapper,
            McpServerStreamableHttpProperties properties) {
        return WebMvcStreamableServerTransportProvider.builder()
                .jsonMapper(new JacksonMcpJsonMapper(jsonMapper))
                .mcpEndpoint(properties.getMcpEndpoint())
                .keepAliveInterval(properties.getKeepAliveInterval())
                .disallowDelete(properties.isDisallowDelete())
                .contextExtractor(request -> {
                    String authorization = request.headers().firstHeader(HttpHeaders.AUTHORIZATION);
                    if (!StringUtils.hasText(authorization)) {
                        return McpTransportContext.EMPTY;
                    }
                    return McpTransportContext.create(Map.of(
                            HttpHeaders.AUTHORIZATION,
                            authorization
                    ));
                })
                .build();
    }
}
