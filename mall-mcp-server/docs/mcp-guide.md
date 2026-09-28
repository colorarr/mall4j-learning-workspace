# MCP 学习与项目实践手册

> 本文用于记录 `mall-mcp-server` 的 MCP 基础知识、技术选择、配置方式和排错方法。  
> 当前项目基线：Spring Boot 4.1.1、Spring AI 2.0.1、MCP 协议版本 2025-06-18。

## 1. 当前项目定位

商城系统划分为三个独立部分：

```text
用户 / 前端
    │
    ▼
mall-agent（Python）
LangChain + LangGraph
    │
    │ MCP Streamable HTTP
    ▼
mall-mcp-server（Java）
    │
    │ 调用商城业务能力
    ▼
mall4j Java 后端
```

职责划分：

- `mall-agent`：理解用户意图、编排智能体、决定调用哪个工具。
- `mall-mcp-server`：将购物车、商品、订单、客服等 Java 能力封装成 MCP Tool。
- `mall4j`：继续负责原有商城业务、数据库和事务。
- Python 不重复实现 Java 中已经存在的商城业务逻辑。

## 2. MCP 是什么

MCP（Model Context Protocol）是一套让 AI 应用统一调用外部能力的协议。

MCP 主要角色：

```text
MCP Host
  └── MCP Client
         └── MCP Server
                ├── Tools
                ├── Resources
                └── Prompts
```

- **Host**：承载智能体的应用，本项目中是 Python 智能体服务。
- **Client**：Host 内部负责连接 MCP Server 的客户端。
- **Server**：对外暴露工具、资源和提示词的服务，本项目中是 Java 服务。

MCP 消息使用 JSON-RPC 2.0 表示，常见消息包括：

- Request：带 `id`，需要对方返回结果。
- Response：返回与 Request 相同的 `id`。
- Notification：没有 `id`，不要求返回业务结果。

## 3. Tool、Resource、Prompt 的区别

| 能力 | 含义 | 商城示例 |
|---|---|---|
| Tool | 可以执行的操作 | 查询购物车、加入购物车、取消订单 |
| Resource | 可以读取的资源 | 商品说明、售后政策、店铺规则 |
| Prompt | 服务端提供的提示词模板 | 售后回复模板、商品推荐模板 |

当前商城智能体优先使用 **Tool**，因此配置中只开启 Tool 能力。

## 4. 常见传输方式

### 4.1 STDIO

客户端启动 MCP Server 子进程，通过标准输入和标准输出交换消息。

```text
MCP Client ──stdin/stdout── MCP Server Process
```

适合：

- 本地桌面应用和 IDE 插件。
- 单个客户端独享一个 MCP Server 进程。
- 本地文件、命令行等工具。
- 快速原型验证。

特点：无需端口、配置简单，但不适合独立部署、跨机器调用和多客户端共享。

### 4.2 SSE（旧方案）

通过 HTTP POST 发送消息，通过 Server-Sent Events 保持服务端推送通道。

适合：

- 兼容只支持旧版 HTTP+SSE 的 MCP 客户端。
- 维护已有的旧版 MCP 服务。

Spring AI 2.0 已建议新项目使用 Streamable HTTP，SSE 主要用于兼容旧系统。

### 4.3 Streamable HTTP

使用一个 MCP 端点处理 HTTP POST 和 GET，并且可以按需返回普通 JSON 或 SSE 流。

```text
POST /mcp  发送请求、通知或响应
GET  /mcp  可选的服务端消息流
```

适合：

- Python 智能体调用独立的 Java MCP Server。
- 跨语言、跨进程、跨机器调用。
- 多个客户端共享同一个服务。
- Docker、Kubernetes、网关和负载均衡环境。
- 需要认证、监控和服务治理的项目。

这是当前项目采用的方式。

### 4.4 STATELESS 模式

`STATELESS` 是偏无状态部署的 Streamable HTTP 模式，每次请求相互独立。

适合：

- 工具调用完全是独立的请求—响应。
- 服务端不需要主动向客户端发送请求或通知。
- Kubernetes 多副本和水平扩容。
- 不希望维护会话或会话粘性。

当前学习阶段保留 `STREAMABLE`，熟悉完整初始化和会话流程后，再根据部署方式考虑 `STATELESS`。

## 5. 当前项目为什么选择 Streamable HTTP

本项目的 Python 智能体与 Java MCP Server 是两个独立服务：

```text
mall-agent        http://localhost:18081/mcp        mall-mcp-server
  Python       ─────────────────────────────────▶       Java
```

选择理由：

1. Python 与 Java 可以独立开发和启动。
2. Python 不需要负责启动 Java 子进程。
3. 后续可以独立部署到不同服务器。
4. 容易接入认证、日志、监控和网关。
5. 一个 Java MCP Server 可以服务多个智能体客户端。

## 6. MCP 生命周期

典型调用顺序：

```text
1. initialize
       ↓
2. 服务端返回协议版本、能力和 Session ID
       ↓
3. notifications/initialized
       ↓
4. tools/list
       ↓
5. tools/call
       ↓
6. 持续调用或关闭连接
```

### initialize

客户端向服务端声明：

- 支持的协议版本。
- 客户端名称和版本。
- 客户端 capabilities。

服务端返回：

- 双方最终协商的协议版本。
- 服务端名称和版本。
- 服务端 capabilities。
- 可选的 `Mcp-Session-Id`。

### tools/list

获取服务端提供的工具定义，包括：

- 工具名称。
- 工具描述。
- 参数 JSON Schema。

### tools/call

调用具体工具，并传入符合工具 Schema 的参数。

## 7. Mcp-Session-Id

`Mcp-Session-Id` 是 MCP **传输层会话标识**，用于把一个客户端的多次 HTTP 请求关联为同一个逻辑会话。

它可能关联：

- 已协商的协议版本。
- 客户端和服务端 capabilities。
- 当前客户端的 SSE 通道。
- 服务端通知和临时传输状态。
- 断线恢复信息。

初始化成功后，服务端可能返回：

```http
Mcp-Session-Id: 1f7b3aaa-4953-4c88-9b4d-b641cc8540f4
```

后续请求需要携带：

```http
Mcp-Session-Id: 1f7b3aaa-4953-4c88-9b4d-b641cc8540f4
MCP-Protocol-Version: 2025-06-18
```

常见状态：

- 缺少必要的 Session ID：通常返回 `400 Bad Request`。
- Session ID 已失效：通常返回 `404 Not Found`。
- 收到 `404` 后，客户端应重新执行 `initialize`。
- 客户端结束时可以通过 DELETE 请求通知服务端结束会话。

正规 MCP Client 会自动保存和携带 Session ID，业务代码通常不需要手动维护。

### 不要混淆三种 ID

| 标识 | 职责 |
|---|---|
| `Mcp-Session-Id` | MCP 客户端与服务器之间的传输会话 |
| `Authorization` / Token | 商城登录用户的身份和权限 |
| LangGraph `thread_id` | 智能体对话状态和长期/短期记忆 |

`Mcp-Session-Id` 不能代替商城登录 Token，也不应该作为查询用户购物车的依据。

## 8. 当前 Maven 依赖

Spring AI 使用 BOM 统一管理依赖版本：

```xml
<properties>
    <java.version>17</java.version>
    <spring-ai.version>2.0.1</spring-ai.version>
</properties>

<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>org.springframework.ai</groupId>
            <artifactId>spring-ai-bom</artifactId>
            <version>${spring-ai.version}</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
    </dependencies>
</dependencyManagement>
```

核心依赖：

```xml
<dependency>
    <groupId>org.springframework.ai</groupId>
    <artifactId>spring-ai-starter-mcp-server-webmvc</artifactId>
</dependency>
```

辅助依赖：

- `spring-boot-starter-validation`：参数校验。
- `spring-boot-starter-actuator`：健康检查。
- `spring-boot-starter-test`：测试。

## 9. 当前服务配置

```yaml
spring:
  application:
    name: mall-mcp-server
  ai:
    mcp:
      server:
        name: mall-mcp-server
        version: 0.0.1
        type: SYNC
        protocol: STREAMABLE
        instructions: "提供商城购物车、订单、商品和客服相关工具"
        capabilities:
          tool: true
          resource: false
          prompt: false
          completion: false
        annotation-scanner:
          enabled: true
        streamable-http:
          mcp-endpoint: /mcp

server:
  port: 18081
```

配置含义：

- `type: SYNC`：注册同步 Java 工具方法。
- `protocol: STREAMABLE`：使用 Streamable HTTP。
- `mcp-endpoint: /mcp`：MCP 统一端点。
- `annotation-scanner.enabled: true`：自动扫描 MCP 注解。
- 当前只开启 Tool 能力。

## 10. Spring AI MCP Tool 形式

Spring AI 2.0.1 支持使用注解声明工具：

```java
import org.springframework.ai.mcp.annotation.McpTool;
import org.springframework.ai.mcp.annotation.McpToolParam;
import org.springframework.stereotype.Component;

@Component
public class ExampleTools {

    @McpTool(name = "example_echo", description = "返回输入的测试工具")
    public String echo(
            @McpToolParam(description = "需要返回的内容", required = true)
            String content) {
        return content;
    }
}
```

关键点：

1. 工具类必须成为 Spring Bean，例如使用 `@Component`。
2. 方法使用 `@McpTool`。
3. 参数使用 `@McpToolParam` 描述用途和必填性。
4. 工具名称应该稳定、清晰，建议使用 `业务_动作` 格式。
5. 工具描述要告诉模型什么时候调用，而不是只重复方法名。

商城工具名称示例：

```text
cart_get
cart_add_item
cart_remove_item
order_list
order_get_detail
order_cancel
product_search
product_get_detail
```

## 11. 验证方式

### 11.1 健康检查

浏览器或终端访问：

```bash
curl http://localhost:18081/actuator/health
```

预期：

```json
{"groups":["liveness","readiness"],"status":"UP"}
```

### 11.2 MCP 初始化

```bash
curl -i -X POST http://localhost:18081/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2025-06-18",
      "capabilities": {},
      "clientInfo": {
        "name": "curl-test",
        "version": "1.0.0"
      }
    }
  }'
```

正常响应应该包含：

- HTTP 状态码 `200`。
- 响应头 `Mcp-Session-Id`。
- JSON 中的 `serverInfo` 和 `capabilities`。

### 11.3 为什么浏览器打开 `/mcp` 会报错

浏览器地址栏发送普通 GET 请求，通常携带：

```http
Accept: text/html
```

而 Streamable HTTP 的 GET 消息流要求：

```http
Accept: text/event-stream
```

所以浏览器直接打开 `/mcp` 时可能看到：

```text
Invalid Accept header. Expected TEXT_EVENT_STREAM
```

这不表示服务启动失败。浏览器应访问 `/actuator/health`；`/mcp` 应使用 MCP Client 或正确配置的 `curl` 验证。

## 12. 常见问题速查

### 服务启动但 `/mcp` 浏览器报 Accept 错误

原因：浏览器把 MCP 协议端点当成普通网页访问。  
处理：使用 MCP Client 或带正确 `Accept` 请求头的 `curl`。

### 返回 400 Bad Request

常见原因：

- 请求体不是合法 JSON-RPC。
- 缺少 `Content-Type: application/json`。
- 缺少正确的 `Accept`。
- 初始化之后未携带 Session ID。
- `MCP-Protocol-Version` 不受支持。

### 返回 404 Session Not Found

常见原因：

- Java MCP Server 已重启。
- Session 已超时或被清理。
- 使用了其他客户端生成的 Session ID。

处理：重新发送 `initialize` 获取新 Session ID。

### tools/list 是空数组

常见原因：

- 还没有编写 `@McpTool` 方法。
- 工具类不是 Spring Bean。
- 工具类不在 Spring 扫描包路径内。
- 配置关闭了 Tool capability。
- SYNC 服务中声明了只适用于 ASYNC 的工具。

### Python 调用时是否要手动处理 Session ID

通常不需要。标准 MCP Client 会自动处理初始化、Session ID 和协议版本请求头。

## 13. 认证和会话边界

MCP 传输本身不等于商城用户认证。后续接入真实业务时需要单独处理：

```text
Authorization: Bearer <商城用户Token>
```

推荐边界：

1. Python 智能体从用户请求获得身份上下文。
2. Python MCP Client 调用 Java MCP Server 时传递 Authorization。
3. Java MCP Server 校验 Token 或把 Token 传递给原商城后端。
4. Java 业务层根据认证结果确定用户，不能信任模型自由生成的用户 ID。

`Mcp-Session-Id` 只负责 MCP 会话关联，不负责用户权限认证。

## 14. 当前项目决定

- MCP Server 与原 Java 商城后端保持独立。
- Python 智能体与 MCP Server 使用 Streamable HTTP。
- 当前先使用同步工具：`type: SYNC`。
- 采用 Spring AI 的 `@McpTool` 注解，减少手动注册代码。
- 当前仅开放 Tool capability。
- 第一阶段使用模拟数据验证完整链路。
- 链路稳定后，再对接真实 Java 商城业务。
- 用户身份、MCP Session、LangGraph Thread 分别管理。

## 15. 后续实践顺序

建议按照以下顺序继续：

```text
1. 编写最简单的 echo MCP Tool
2. 使用 MCP Client 验证 tools/list 和 tools/call
3. 编写模拟 cart_get 工具
4. Python 连接 mall-mcp-server
5. cart_agent 调用 cart_get
6. 接入用户认证上下文
7. 替换为真实商城购物车业务
8. 增加商品、订单和客服工具
9. 增加超时、错误码、日志和监控
10. 考虑生产环境鉴权和多实例部署
```

## 16. 官方资料

- [MCP 官方文档](https://modelcontextprotocol.io/)
- [MCP 2025-06-18 Streamable HTTP 规范](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports)
- [Spring AI MCP 概览](https://docs.spring.io/spring-ai/reference/api/mcp/mcp-overview.html)
- [Spring AI MCP Server Starter](https://docs.spring.io/spring-ai/reference/api/mcp/mcp-server-boot-starter-docs.html)
- [Spring AI MCP 快速入门](https://docs.spring.io/spring-ai/reference/guides/getting-started-mcp.html)

---

最后更新：2026-09-28
