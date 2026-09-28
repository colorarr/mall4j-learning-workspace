# Mall4j 前端项目

本目录与后端项目 `../mall4j` 同级，前端不参与后端 Maven 构建。

| 项目 | 用途 | 开发命令 |
| --- | --- | --- |
| `mall4v` | Vue 管理后台 | `pnpm install && pnpm run dev` |
| `mall4uni` | H5、App 等用户端 | 以项目 `package.json` 为准 |
| `mall4m` | 原生微信小程序 | 使用微信开发者工具打开 |

后端统一地址：`http://127.0.0.1:8080`。

- `mall4v`、`mall4uni`：修改各自 `.env.*` 的 `VITE_APP_BASE_API`。
- `mall4m`：修改 `utils/config.js` 的 `domain`。

后端启动入口：`../mall4j/yami-shop-admin/src/main/java/com/yami/shop/admin/WebApplication.java`。
