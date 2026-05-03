<div align="center">

# Gerrit MCP

[Forge](https://github.com/zjio26/forge) で開発

AIアシスタントと[Gerrit](https://www.gerritcodereview.com/)コードレビューシステムを繋ぐ[Model Context Protocol](https://modelcontextprotocol.io/)サーバー。

**変更の照会 · コードレビュー · プロジェクト管理 — すべて自然言語で。**

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-compatible-green.svg)](https://modelcontextprotocol.io/)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)

[English](README.md) · [中文](README.zh-CN.md) · [Español](README.es.md)

</div>

---

## 機能

- **変更管理** — 変更の照会、レビュー、サブミット、破棄、復元、リベース
- **プロジェクト閲覧** — プロジェクト、ブランチ、タグの一覧表示
- **アカウント検索** — ユーザープロフィールと認証済みユーザーの照会
- **レビュアーワークフロー** — 変更へのレビュアーの追加と一覧表示
- **コメントアクセス** — 変更のインラインコメントの読み取り
- **読み取り専用モード** — すべての書き込み操作をブロックする安全なデプロイ
- **マルチトランスポート** — stdio、SSE、Streamable HTTPをすぐに利用可能

## クイックスタート

### uvxで実行（クローン不要）

```bash
# uvのインストール（未インストールの場合）
# curl -LsSf https://astral.sh/uv/install.sh | sh

# GitHubから直接実行 — クローンやインストール不要
GERRIT_URL=https://gerrit.example.com \
GERRIT_USERNAME=your-username \
GERRIT_PASSWORD=your-http-password \
MCP_TRANSPORT=stdio \
uvx --from git+https://github.com/zjio26/gerrit-mcp.git gerrit-mcp
```

### ローカルインストール

```bash
# クローンしてuvでインストール（推奨）
git clone https://github.com/zjio26/gerrit-mcp.git
cd gerrit-mcp
uv pip install -e .

# またはpipを使用
pip install -e .
```

### 設定

Gerrit認証情報を記載した`.env`ファイルを作成：

```bash
GERRIT_URL=https://gerrit.example.com
GERRIT_USERNAME=your-username
GERRIT_PASSWORD=your-http-password
```

> Gerrit → Settings → HTTP Password でHTTPパスワードを生成してください。

### 実行

```bash
# デフォルト：Streamable HTTP、http://0.0.0.0:8000 で待機
python -m gerrit_mcp

# stdioトランスポート（Claude Desktopなど）
MCP_TRANSPORT=stdio python -m gerrit_mcp

# SSEトランスポート
MCP_TRANSPORT=sse python -m gerrit_mcp
```

### Docker

```bash
docker build -t gerrit-mcp .
docker run --env-file .env -p 8000:8000 gerrit-mcp

# 別のトランスポートを指定する場合
docker run --env-file .env -e MCP_TRANSPORT=stdio gerrit-mcp
```

## MCPツール

### 変更

| ツール | 説明 | 書込 |
|--------|------|:----:|
| `gerrit_query_changes` | Gerritクエリ構文で変更を検索 | |
| `gerrit_get_change` | 特定の変更の詳細情報を取得 | |
| `gerrit_get_change_detail` | すべてのリビジョン情報を含む変更詳細を取得 | |
| `gerrit_get_change_comments` | 変更のコメント一覧を取得 | |
| `gerrit_review_change` | 変更をレビュー（スコア + メッセージ） | **W** |
| `gerrit_submit_change` | 変更をマージ用にサブミット | **W** |
| `gerrit_abandon_change` | 変更を破棄 | **W** |
| `gerrit_restore_change` | 破棄された変更を復元 | **W** |
| `gerrit_rebase_change` | 変更をリベース | **W** |
| `gerrit_set_topic` | 変更にトピックを設定 | **W** |
| `gerrit_add_reviewer` | 変更にレビュアーを追加 | **W** |
| `gerrit_list_reviewers` | 変更のレビュアー一覧を取得 | |

### プロジェクト

| ツール | 説明 | 書込 |
|--------|------|:----:|
| `gerrit_list_projects` | 表示可能なプロジェクト一覧 | |
| `gerrit_get_project` | プロジェクトの説明を取得 | |
| `gerrit_list_branches` | プロジェクトのブランチ一覧 | |
| `gerrit_list_tags` | プロジェクトのタグ一覧 | |

### アカウント

| ツール | 説明 | 書込 |
|--------|------|:----:|
| `gerrit_get_self_account` | 認証済みユーザーのアカウント情報を取得 | |
| `gerrit_get_account` | 名前、メール、IDでアカウントを取得 | |

**W** マークのツールは`MCP_READONLY=true`でブロックされます。

## 設定

| 変数 | 説明 | デフォルト |
|------|------|------------|
| `GERRIT_URL` | GerritサーバーのベースURL | *必須* |
| `GERRIT_USERNAME` | HTTPパスワードのユーザー名 | *必須* |
| `GERRIT_PASSWORD` | HTTPパスワード | *必須* |
| `MCP_TRANSPORT` | トランスポートモード：`stdio`、`sse`、`streamable-http` | `streamable-http` |
| `HOST` | サーバーバインドホスト（HTTPトランスポートのみ） | `0.0.0.0` |
| `PORT` | サーバーバインドポート（HTTPトランスポートのみ） | `8000` |
| `MCP_READONLY` | すべての書き込み操作をブロック | `false` |
| `GERRIT_VERIFY_SSL` | SSL証明書の検証 | `true` |
| `GERRIT_TIMEOUT` | リクエストタイムアウト（秒） | `30` |

## クライアント統合

### Claude Desktop

`claude_desktop_config.json`に追加：

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

### MCPゲートウェイ（Streamable HTTP）

デフォルトの`streamable-http`トランスポートは、MCPゲートウェイ背後での水平スケーリング用に設計されています。プロキシ互換性のため`stateless_http=True`と`json_response=True`を使用。

```bash
# サーバー起動
python -m gerrit_mcp
# MCPエンドポイント：http://localhost:8000/mcp
```

### SSEクライアント

```bash
MCP_TRANSPORT=sse python -m gerrit_mcp
# SSEエンドポイント：http://localhost:8000/sse
```

## 開発

```bash
# 開発依存関係をインストール
uv pip install -e ".[dev]"

# テスト実行
pytest

# 詳細出力
pytest -v
```

## アーキテクチャ

```
src/gerrit_mcp/
├── __init__.py
├── __main__.py          # エントリポイント：python -m gerrit_mcp
├── server.py            # FastMCPアプリ、トランスポート設定、ライフサイクル
├── config.py            # pydantic-settings、環境変数
├── gerrit_client.py     # 非同期Gerrit REST APIクライアント（httpx）
├── models.py            # Pydanticリクエスト/レスポンスモデル
└── tools/
    ├── __init__.py      # 共有ヘルパー：_format_result, _handle_error, _require_writable
    ├── changes.py       # 変更関連MCPツール
    ├── projects.py      # プロジェクト関連MCPツール
    └── accounts.py      # アカウント関連MCPツール
```

## ライセンス

MIT
