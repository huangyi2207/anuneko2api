# Anuneko OpenAI Proxy

[English](./README.md)

将 Anuneko 服务转换为标准 OpenAI API 格式的代理服务。

## ✨ 项目特色

*   **完全兼容**：支持 OpenAI 格式的流式 (Stream) 与非流式响应，完美适配主流客户端。
*   **智能会话**：基于对话上下文自动管理 Anuneko 后台 `chat_id`，实现无感知的连续对话。
*   **多模型支持**：支持通过模型名称自动切换“橘猫”与“黑猫”。
*   **安全隔离**：支持自定义 API Key 进行访问控制。

## 🚀 快速部署 (Docker)

1. 创建配置文件 `.env`：
   ```dotenv
   ANUNEKO_TOKEN=你的_x-token
   PROXY_API_KEYS=["sk-你的key1", "sk-你的key2"]
   ```

2. 启动容器：
   ```bash
   docker run -d -p 8000:8000 --env-file .env --name anuneko-proxy ghcr.io/your-repo/anuneko-proxy:latest
   ```
   *(或者手动构建: `docker build -t anuneko-proxy .`)*

## ⚙️ 配置说明

### 环境变量 (.env)
| 变量名 | 说明 | 示例 |
| :--- | :--- | :--- |
| `ANUNEKO_TOKEN` | **必填**，Anuneko 的 x-token | `eyJh...` |
| `ANUNEKO_COOKIE` | 选填，部分账号可能需要 Cookie | `session=...` |
| `PROXY_API_KEYS` | 客户端连接此服务时验证用的 Key | `["sk-123456"]` |

### 客户端连接设置 (如 NextChat)
*   **接口地址**: `http://服务器IP:8000` (若客户端强制加/v1，则不需要手动加)
*   **API Key**: 填写你在 `PROXY_API_KEYS` 中设置的值 (如 `sk-123456`)
*   **自定义模型**: `orange-cat` (橘猫), `black-cat` (黑猫)

## ⚠️ 免责声明

本项目仅供技术研究和学习使用。
1. 本服务只是第三方前端封装，不存储任何数据，所有请求直接转发至原服务。
2. 请勿将本项目用于商业用途或任何非法用途。
3. 因使用本项目导致的账号封禁或其他损失，开发者不承担任何责任。

## 📄 开源协议

本项目遵循 [GNU General Public License v3.0 (GPLv3)](./LICENSE) 协议。
