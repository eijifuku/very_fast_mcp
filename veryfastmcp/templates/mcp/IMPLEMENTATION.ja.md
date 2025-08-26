# IMPLEMENTATION GUIDE (MCP server & tools)

このドキュメントは、`vfmcp new` で生成された **MCP サーバ雛形**上で、
ツールの実装を進めるための実装ガイドです。

## 0) セットアップ
```bash
vfmcp new my-mcp
cd my-mcp
pip install -e .[mcp]   # fastmcp / PyYAML
```

## 1) 起動（stdio / http の切り替え）
起動設定は `configs/server.yaml` の **run_options** を編集します。
これらは `mcp_server.py` から **`mcp.run(**run_options)`** にそのまま渡されます。

```yaml
# configs/server.yaml
run_options:
  transport: stdio
  # 例: http にする場合
  # transport: http
  # host: 127.0.0.1
  # port: 8000
  # path: /mcp
```

```bash
python mcp_server.py   # 既定: stdio
```

## 2) ツールの追加（ジェネレータ）
```bash
vfmcp generate tool Search
```

以下が生成されます:
```
mcp_app/tools/search.py
tests/test_search.py
```

`mcp_app/tools/search.py` にビジネスロジックを実装します（雛形は `run(dict) -> Any`）:

```python
# mcp_app/tools/search.py（例）
class SearchTool:
    """Business logic for 'search'."""
    
    # ツールの基本情報
    name = "search"
    description = "Search for documents or content"
    
    async def run(self, params: dict):
        query = (params or {}).get("query")
        if not query:
            raise ValueError("missing 'query'")
        # TODO: 実装
        return {"results": [f"you searched: {query}"]}

**重要な属性:**
- `name`: ツールの識別名（MCPクライアントから呼び出し時に使用）
- `description`: ツールの説明（MCPクライアントのツール一覧で表示される）
- `run()`: ツール実行時のメインロジック（非同期関数）

## 3) MCP への公開（自動登録 or 手動登録）
`mcp_server.py` には次のマーカーがあります:
```python
# AUTO-REGISTER MARKER (do not remove): {VFMCP-AUTO-REGISTER}
```

`vfmcp generate tool <Name>` 実行時、CLI がこのマーカー直後に
公開関数を**自動追記**します（冪等に配慮）。

自動登録が無い/失敗した場合は、手動で以下を `mcp_server.py` に追記します:

```python
from mcp_app.tools.search import SearchTool

@mcp.tool(name="search")
async def search(**kwargs):
    return await SearchTool().run(kwargs)
```

> 公開名は `@mcp.tool(name="…")` で決まります。関数名も合わせると分かりやすいです。

## 4) テスト
雛形には pytest 用の簡易テストが入っています。ツールを追加したらテストも追加しましょう。

```bash
pytest -q
```

例（`tests/test_search.py` をベースに）:
```python
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

## 5) クライアントからの利用（例）
- **stdio**: Claude Desktop / MCP Inspector の「起動コマンド」に `python mcp_server.py` を登録
- **http**: `run_options.transport=http` に変更し、`http://host:port/path` を MCP クライアントのリモート接続に設定

## 6) FAQ
- **入力スキーマを厳密にしたい**  
  依存追加が許容されるなら Pydantic を導入。最小構成のままなら `run()` の冒頭で手書き検証でもOK。
- **ツール名や公開名を変えたい**  
  ビジネスロジックのクラス名は任意。公開名は `@mcp.tool(name="...")` を変更。
- **複数ツール**  
  `vfmcp generate tool Xxx` を繰り返し、`mcp_server.py` に `@mcp.tool` を増やす（自動登録が有効なら自動で追記）。
