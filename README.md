# Mall4j Learning Workspace

这是一个用于商城学习、功能验证与本地二次开发的多组件工作区，**不是 Mall4j 官方发布仓库，也不代表 Mall4j 官方立场**。

## 来源与许可说明

- `mall4j/` 中的商城后端及配套文档来源于 [gz-yami/mall4j](https://github.com/gz-yami/mall4j)，在其基础上学习和修改。上游仓库当前标注 **GNU AGPL-3.0**；上游的 `LICENSE`、版权及来源声明随代码保留。对该部分进行复制、修改、分发或通过网络提供服务时，请阅读并按该许可证履行相应义务。
- `front-end/mall4v/`、`front-end/mall4uni/`、`front-end/mall4m/` 是该商城配套的管理端、用户端和微信小程序前端，目录内保留各自上游许可证及说明。请以各目录中的 `LICENSE` 和上游仓库说明为准。
- `mall-agent/` 与 `mall-mcp-server/` 是本工作区中的独立配套组件。其依赖、第三方素材与代码应分别依据各自文件及依赖声明确认；本 README **不为这些组件或上游代码额外授予许可**。
- 本工作区为学习和二次开发整理，不声称拥有上游 Mall4j 代码的权利，不暗示与上游作者存在合作、背书或官方关联。上游有更新时，以其仓库与许可证文本为准。

为尊重来源，保留各组件中的上游 `LICENSE`、版权标记和来源信息；新增或修改内容请在提交记录或文件说明中标注，避免被误认为上游官方发布。

## 目录结构

| 目录 | 内容 |
| --- | --- |
| `mall4j/` | Mall4j Java 后端、数据库脚本、部署资料与上游文档 |
| `front-end/mall4v/` | Vue 管理后台 |
| `front-end/mall4uni/` | uni-app 用户端 |
| `front-end/mall4m/` | 微信小程序用户端 |
| `mall-agent/` | Python 商城智能体实验项目 |
| `mall-mcp-server/` | Java MCP Server 实验项目 |

## 开发提示

各组件的运行环境和命令以组件 README、配置文件及上游文档为准。商城前后端的入口和本地 API 地址见 [`front-end/README.md`](front-end/README.md)；后端部署资料见 [`mall4j/README.md`](mall4j/README.md)。不要将个人 `.env`、小程序私有配置、密钥或本机构建产物提交到版本库。

## 在线测试

- 用户端地址：[https://mall.zpzhub.shop](https://mall.zpzhub.shop)
- 测试账号：用户名 `color`，密码 `123456789`

该账号用于商城功能测试，请勿用于正式业务。

## 上游项目

- [Mall4j GitHub 仓库](https://github.com/gz-yami/mall4j)
- 上游仓库许可证：[`mall4j/LICENSE`](mall4j/LICENSE)
