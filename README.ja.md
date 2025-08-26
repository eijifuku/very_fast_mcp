# VeryFastMCP (vfmcp)

FastMCPのための「超高速」スキャフォールディング＆ジェネレーター。コマンド一発でMCPサーバーの完全なスケルトンを生成し、サーバー設定やルーティングなどの煩雑な作業を自動化。開発者はビジネスロジックの実装だけに集中でき、数分で本番稼働可能なMCPサーバーを構築できます。

## 機能
- **スキャフォールド**: `vfmcp new <dir>` で`configs/server.yaml`と`mcp_server.py`を含むMCPサーバーの骨組みを作成します。
- **ジェネレーター**: `vfmcp generate tool <Name>` でツールとそのテストを追加します。
- **テンプレート同梱**: `veryfastmcp/templates/{mcp,tool}`

## インストール

```bash
# GitHubからインストール
pip install git+https://github.com/username/very_fast_mcp.git

# またはソースからインストール
git clone https://github.com/username/very_fast_mcp.git
cd very_fast_mcp
pip install -e .
```

インストール後、`vfmcp`コマンドがPATHから利用可能になります。

## クイックスタート

```bash
python -m veryfastmcp --help
python -m veryfastmcp new my-mcp # 新規プロジェクトを作成
python -m veryfastmcp generate tool Search -C my-mcp  # または先にcd my-mcpを実行
```

### 生成されたプロジェクト

```bash
pip install -e .[mcp]
python mcp_server.py
```

`configs/server.yaml`を編集して`run_options`を変更できます（`mcp.run(**run_options)`に渡されます）。

## 実装ガイド（MCPサーバ＆ツールの作り方）

詳細な手順は [`veryfastmcp/templates/mcp/IMPLEMENTATION.md`](veryfastmcp/templates/mcp/IMPLEMENTATION.md) を参照してください。

### 0) セットアップ
```bash
vfmcp new my-mcp
cd my-mcp
pip install -e .[mcp]  # fastmcp / PyYAML を導入
```

### 1) 起動（stdio / http の切り替え）

`configs/server.yaml` の **run_options** が `mcp.run(**run_options)` にそのまま渡されます。

```yaml
# configs/server.yaml
run_options:
  transport: stdio
  # transport: http
  # host: 127.0.0.1
  # port: 8000
  # path: /mcp
```

```bash
python mcp_server.py   # 既定: stdio
```

### 2) ツールの追加（ジェネレータ）

```bash
vfmcp generate tool Search
```

以下が生成されます:

```
mcp_app/tools/search.py
tests/test_search.py
```

`mcp_app/tools/search.py`（ビジネスロジック本体）に実装を書きます：

```python
# mcp_app/tools/search.py（例）
class SearchTool:
    """Business logic for 'search'."""
    async def run(self, params: dict):
        query = (params or {}).get("query")
        if not query:
            raise ValueError("missing 'query'")
        # TODO: 実装
        return {"results": [f"you searched: {query}"]}
```

### 3) MCP への公開（自動登録 or 手動登録）

`mcp_server.py` には次のマーカーがあります：

```python
# AUTO-REGISTER MARKER (do not remove): {VFMCP-AUTO-REGISTER}
```

`vfmcp generate tool <Name>` 実行時に、この直後へ `@mcp.tool` 関数を**自動追記**します（CLIが対応している場合）。

手動で登録する場合は、以下を `mcp_server.py` に追記：

```python
from mcp_app.tools.search import SearchTool

@mcp.tool(name="search")
async def search(**kwargs):
    return await SearchTool().run(kwargs)
```

### 4) テスト

```bash
pytest -q
```

サンプル：

```python
# tests/test_search.py の例
import pytest
from mcp_app.tools.search import SearchTool

@pytest.mark.asyncio
async def test_search_ok():
    out = await SearchTool().run({"query": "hello"})
    assert "results" in out

@pytest.mark.asyncio
async def test_search_ng():
    with pytest.raises(ValueError):
        await SearchTool().run({})
```

### 5) クライアントからの利用

* **stdio**: Claude Desktop / MCP Inspector の「起動コマンド」に `python mcp_server.py`
* **http**: `run_options.transport=http` に変更し、`http://host:port/path` を MCP クライアントのリモート接続に設定

### 6) MCPクライアントでの設定方法

#### Cursorでの設定

`.cursor/mcp.json`ファイルを作成または編集して、作成したMCPサーバーを追加します：

```json
{
  "mcpServers": {
    "my-mcp-server": {
      "command": "python",
      "args": ["mcp_server.py"],
      "cwd": "/path/to/your/mcp/project"
    }
  }
}
```

**stdioモードの場合（推奨）:**
```json
{
  "mcpServers": {
    "my-mcp-server": {
      "command": "python",
      "args": ["mcp_server.py"],
      "cwd": "/path/to/your/mcp/project"
    }
  }
}
```

**httpモードの場合:**
```json
{
  "mcpServers": {
    "my-mcp-server": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

#### その他のMCPクライアント

- **Claude Desktop**: 設定画面でMCPサーバーを追加
- **MCP Inspector**: 起動コマンドまたはURLを指定
- **VS Code**: MCP拡張機能の設定でサーバーを追加

**注意**: `cwd`（カレントワーキングディレクトリ）は、MCPサーバープロジェクトのルートディレクトリを指定してください。

#### DockerコンテナでMCPサーバーを動かす場合

**stdioモード（Docker経由）:**
```json
{
  "mcpServers": {
    "my-mcp-docker": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "my-mcp-server:latest"],
      "cwd": "/path/to/your/mcp/project"
    }
  }
}
```

**httpモード（Docker経由）:**
```json
{
  "mcpServers": {
    "my-mcp-docker": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```


**Dockerビルドと実行:**
```bash
# イメージをビルド
docker build -t my-mcp-server .

# コンテナを起動（stdioモード）
docker run --rm -i my-mcp-server:latest

# コンテナを起動（httpモード）
docker run --rm -p 8000:8000 my-mcp-server:latest
```

## コマンド

### `new <dir> [--force]`

* `templates/mcp/`を`<dir>`に展開します。
* `--force`が指定されていない場合、`<dir>`にファイルが存在するとエラーになります。

### `generate tool <Name> [--force]`

* `templates/tool/*.j2`から以下を生成します：
  * `mcp_app/tools/<name>.py`
  * `tests/test_<name>.py`
* `--force`が指定されていない場合、ファイルが既に存在するとエラーになります。

## プロジェクト構成

```
veryfastmcp/
  __init__.py
  __main__.py            # python -m veryfastmcp のエントリーポイント
  cli.py                 # argparseベースのCLI
  templates/
    mcp/                 # MCPサーバーのスケルトン
      __init__.py
      __main__.py
      mcp_server.py
      configs/server.yaml
      mcp_app/...
      tests/...
    tool/                # ジェネレーターテンプレート
      tool.py.j2
      test_tool.py.j2
scripts/
  (なし)
tests/
  test_cli.py            # CLIのサブプロセステスト
pyproject.toml
README.md
```

## ライセンス

MIT