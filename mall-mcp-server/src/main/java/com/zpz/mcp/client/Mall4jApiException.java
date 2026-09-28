package com.zpz.mcp.client;

/**
 * 调用 mall4j REST API 失败时抛出的异常。
 */
public class Mall4jApiException extends RuntimeException {

    /**
     * 创建 mall4j API 调用异常。
     *
     * @param message 可展示的错误信息
     */
    public Mall4jApiException(String message) {
        super(message);
    }

    /**
     * 创建包含原始异常的 mall4j API 调用异常。
     *
     * @param message 可展示的错误信息
     * @param cause 原始异常
     */
    public Mall4jApiException(String message, Throwable cause) {
        super(message, cause);
    }
}
