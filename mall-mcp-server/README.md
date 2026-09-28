# mall-mcp-server

商城智能体使用的独立 Java MCP Server。

## 当前技术栈

- Java 17
- Spring Boot 4.1.1
- Spring AI 2.0.1
- Spring Cloud OpenFeign
- MCP Streamable HTTP
- 服务端口：`18081`
- MCP 端点：`http://localhost:18081/mcp`
- 健康检查：`http://localhost:18081/actuator/health`

## 项目文档

- [MCP 学习与项目实践手册](docs/mcp-guide.md)

## 启动

先启动 mall4j 用户端后端（默认 `http://127.0.0.1:18080`），再启动 MCP Server：

```bash
mvn spring-boot:run
```

需要连接其他 mall4j 地址时：

```bash
MALL4J_BASE_URL=http://HOST:18080 mvn spring-boot:run
```

调用关系：

```text
Python Agent -> MCP Streamable HTTP -> mall-mcp-server -> OpenFeign -> mall4j REST API
```

MCP Server 独立运行。MCP Server 停止不会影响 mall4j 原有商城接口。

OpenFeign 默认连接超时为 2 秒、读取超时为 5 秒，配置位于
`src/main/resources/application.yaml`。

## 验证

```bash
curl http://localhost:18081/actuator/health
```

`/mcp` 是协议端点，不是网页地址。不要使用浏览器地址栏直接验证，应该使用 MCP 客户端或带有正确请求头的 `curl` 请求。
