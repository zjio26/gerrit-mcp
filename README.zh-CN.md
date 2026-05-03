<div align="center">

# Gerrit MCP

使用 [Forge](https://github.com/zjio26/forge) 开发

一个 [Model Context Protocol](https://modelcontextprotocol.io/) 服务器，将 AI 助手与 [Gerrit](https://www.gerritcodereview.com/) 代码审查系统连接起来。

**查询变更 · 审查代码 · 管理项目 — 全部通过自然语言完成。**

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-compatible-green.svg)](https://modelcontextprotocol.io/)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)

[English](README.md) · [日本語](README.ja.md) · [Español](README.es.md)

</div>

---

## 功能特性

- **变更管理** — 查询、审查、提交、放弃、恢复和变基变更
- **项目浏览** — 列出项目、分支和标签
- **账户查询** — 查询用户资料和已认证的自己
- **审查者工作流** — 添加和列出变更审查者
- **评论访问** — 读取任何变更的行内评论
- **只读模式** — 安全部署，阻止所有写操作
- **多传输协议** — 开箱即用支持 stdio、SSE 和 Streamable HTTP

## 快速开始

### 使用 uvx 运行（无需克隆）

```bash
# 安装 uv（如尚未安装）
# curl -LsSf https://astral.sh/uv/install.sh | sh

# 直接从 GitHub 运行 — 无需克隆或安装
GERRIT_URL=https://gerrit.example.com \
GERRIT_USERNAME=your-username \
GERRIT_PASSWORD=your-http-password \
MCP_TRANSPORT=stdio \
uvx --from git+https://github.com/zjio26/gerrit-mcp.git gerrit-mcp
```

### 本地安装

```bash
# 克隆并使用 uv 安装（推荐）
git clone https://github.com/zjio26/gerrit-mcp.git
cd gerrit-mcp
uv pip install -e .

# 或使用 pip
pip install -e .
```

### 配置

创建 `.env` 文件，填入你的 Gerrit 凭证：

```bash
GERRIT_URL=https://gerrit.example.com
GERRIT_USERNAME=your-username
GERRIT_PASSWORD=your-http-password
```

> 在 Gerrit → Settings → HTTP Password 生成 HTTP 密码。

### 运行

```bash
# 默认：Streamable HTTP 模式，监听 http://0.0.0.0:8000
python -m gerrit_mcp

# stdio 传输协议（适用于 Claude Desktop 等）
MCP_TRANSPORT=stdio python -m gerrit_mcp

# SSE 传输协议
MCP_TRANSPORT=sse python -m gerrit_mcp
```

### Docker

```bash
docker build -t gerrit-mcp .
docker run --env-file .env -p 8000:8000 gerrit-mcp

# 或使用其他传输协议
docker run --env-file .env -e MCP_TRANSPORT=stdio gerrit-mcp
```

## MCP 工具

### 变更

| 工具 | 描述 | 写操作 |
|------|------|:-----:|
| `gerrit_query_changes` | 使用 Gerrit 查询语法搜索变更 | |
| `gerrit_get_change` | 获取特定变更的详细信息 | |
| `gerrit_get_change_detail` | 获取包含所有修订信息的变更详情 | |
| `gerrit_get_change_comments` | 列出变更上的评论 | |
| `gerrit_review_change` | 审查变更（评分 + 消息） | **W** |
| `gerrit_submit_change` | 提交变更以合并 | **W** |
| `gerrit_abandon_change` | 放弃变更 | **W** |
| `gerrit_restore_change` | 恢复已放弃的变更 | **W** |
| `gerrit_rebase_change` | 变基变更 | **W** |
| `gerrit_set_topic` | 设置变更主题 | **W** |
| `gerrit_add_reviewer` | 添加审查者到变更 | **W** |
| `gerrit_list_reviewers` | 列出变更上的审查者 | |

### 项目

| 工具 | 描述 | 写操作 |
|------|------|:-----:|
| `gerrit_list_projects` | 列出可见项目 | |
| `gerrit_get_project` | 获取项目描述 | |
| `gerrit_list_branches` | 列出项目的分支 | |
| `gerrit_list_tags` | 列出项目的标签 | |

### 账户

| 工具 | 描述 | 写操作 |
|------|------|:-----:|
| `gerrit_get_self_account` | 获取已认证用户的账户信息 | |
| `gerrit_get_account` | 通过用户名、邮箱或 ID 获取账户 | |

标记为 **W** 的工具在 `MCP_READONLY=true` 时被阻止。

## 配置

| 变量 | 描述 | 默认值 |
|------|------|--------|
| `GERRIT_URL` | Gerrit 服务器基础 URL | *必填* |
| `GERRIT_USERNAME` | HTTP 密码用户名 | *必填* |
| `GERRIT_PASSWORD` | HTTP 密码 | *必填* |
| `MCP_TRANSPORT` | 传输模式：`stdio`、`sse` 或 `streamable-http` | `streamable-http` |
| `HOST` | 服务器绑定主机（仅 HTTP 传输） | `0.0.0.0` |
| `PORT` | 服务器绑定端口（仅 HTTP 传输） | `8000` |
| `MCP_READONLY` | 阻止所有写操作 | `false` |
| `GERRIT_VERIFY_SSL` | 验证 SSL 证书 | `true` |
| `GERRIT_TIMEOUT` | 请求超时时间（秒） | `30` |

## 客户端集成

### Claude Desktop

添加到你的 `claude_desktop_config.json`：

```json
{
  "mcpServers": {
    "gerrit": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/zjio26/gerrit-mcp.git", "gerrit-mcp"],
      "env": {
        "MCP_TRANSPORT": "stdio",
        "GERRIT_URL": "https://gerrit.example.com",
        "GERRIT_USERNAME": "your-username",
        "GERRIT_PASSWORD": "your-http-password"
      }
    }
  }
}
```

### MCP 网关（Streamable HTTP）

默认的 `streamable-http` 传输协议专为 MCP 网关后的水平扩展而设计。使用 `stateless_http=True` 和 `json_response=True` 以兼容代理。

```bash
# 启动服务器
python -m gerrit_mcp
# MCP 端点：http://localhost:8000/mcp
```

### SSE 客户端

```bash
MCP_TRANSPORT=sse python -m gerrit_mcp
# SSE 端点：http://localhost:8000/sse
```

## 开发

```bash
# 安装开发依赖
uv pip install -e ".[dev]"

# 运行测试
pytest

# 详细输出
pytest -v
```

## 架构

```
src/gerrit_mcp/
├── __init__.py
├── __main__.py          # 入口：python -m gerrit_mcp
├── server.py            # FastMCP 应用，传输配置，生命周期
├── config.py            # pydantic-settings，环境变量
├── gerrit_client.py     # 异步 Gerrit REST API 客户端（httpx）
├── models.py            # Pydantic 请求/响应模型
└── tools/
    ├── __init__.py      # 共享工具：_format_result, _handle_error, _require_writable
    ├── changes.py       # 变更相关 MCP 工具
    ├── projects.py      # 项目相关 MCP 工具
    └── accounts.py      # 账户相关 MCP 工具
```

## 许可证

MIT
