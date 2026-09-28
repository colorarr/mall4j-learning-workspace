package com.zpz.mcp.client;

import feign.FeignException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;
import org.springframework.util.StringUtils;
import tools.jackson.databind.JsonNode;
import tools.jackson.databind.json.JsonMapper;

import jakarta.annotation.Resource;
import java.util.function.Supplier;

/**
 * 统一执行 mall4j OpenFeign 请求，并转换 HTTP 和业务异常。
 */
@Component
public class Mall4jClientExecutor {

    private static final Logger LOGGER = LoggerFactory.getLogger(Mall4jClientExecutor.class);

    @Resource
    private JsonMapper jsonMapper;

    /**
     * 执行一次 mall4j 请求并校验统一响应结构。
     *
     * @param operation 不包含敏感信息的操作名称
     * @param request OpenFeign 请求
     * @return mall4j 原始 JSON 响应
     */
    public String execute(String operation, Supplier<String> request) {
        try {
            String response = request.get();
            if (!StringUtils.hasText(response)) {
                return "{}";
            }
            validateBusinessResponse(operation, response);
            return response;
        }
        catch (Mall4jApiException exception) {
            throw exception;
        }
        catch (FeignException exception) {
            int status = exception.status();
            LOGGER.warn("mall4j API request failed: operation={}, status={}", operation, status);
            if (status < 0) {
                throw new Mall4jApiException("商城服务连接失败，请稍后重试", exception);
            }
            String responseBody = exception.contentUTF8();
            String detail = StringUtils.hasText(responseBody) ? "，响应：" + responseBody : "";
            throw new Mall4jApiException("商城接口调用失败，HTTP状态码：" + status + detail, exception);
        }
        catch (RuntimeException exception) {
            LOGGER.error("mall4j API invocation failed: operation={}", operation, exception);
            throw new Mall4jApiException("商城服务调用异常，请稍后重试", exception);
        }
    }

    private void validateBusinessResponse(String operation, String response) {
        try {
            JsonNode root = jsonMapper.readTree(response);
            JsonNode successNode = root.get("success");
            if (successNode != null && !successNode.asBoolean()) {
                JsonNode messageNode = root.get("msg");
                String message = messageNode == null || messageNode.isNull()
                        ? "商城业务处理失败"
                        : messageNode.asString();
                throw new Mall4jApiException(message);
            }
        }
        catch (Mall4jApiException exception) {
            throw exception;
        }
        catch (Exception exception) {
            LOGGER.debug("mall4j response is not a standard response wrapper: operation={}", operation, exception);
        }
    }
}
