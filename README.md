# VeryFastMCP (vfmcp)

*[日本語版はこちら](README.ja.md)*

"Very Fast" scaffolding & generator for FastMCP. Generate a complete MCP server skeleton with a single command, automating server configuration and routing setup. Developers can focus solely on implementing business logic and build production-ready MCP servers in minutes.

## Features
- **Scaffold**: `vfmcp new <dir>` creates an MCP server skeleton with `configs/server.yaml` and `mcp_server.py`.
- **Generator**: `vfmcp generate tool <Name>` adds a tool and its test.
- **Templates bundled**: `veryfastmcp/templates/{mcp,tool}`

## Installation

```bash
# Install globally from PyPI
pip install git+https://github.com/username/very_fast_mcp.git

# Or install from source
git clone https://github.com/username/very_fast_mcp.git
cd very_fast_mcp
pip install -e .
```

After installation, the `vfmcp` command will be available in your PATH.

## Quick Start

```bash
python -m veryfastmcp --help
python -m veryfastmcp new my-mcp # new project
python -m veryfastmcp generate tool Search -C my-mcp  # or cd my-mcp first
```

### Generated project

```bash
pip install -e .[mcp]
python mcp_server.py
```

Edit `configs/server.yaml` to change `run_options` (passed to `mcp.run(**run_options)`).

## Implementation Guide (Creating MCP Server & Tools)

For detailed instructions, see [`veryfastmcp/templates/mcp/IMPLEMENTATION.md`](veryfastmcp/templates/mcp/IMPLEMENTATION.md).

### 0) Setup
```bash
vfmcp new my-mcp
cd my-mcp
pip install -e .[mcp]  # installs fastmcp / PyYAML
```

### 1) Launch (stdio / http switching)

The **run_options** in `configs/server.yaml` are passed directly to `mcp.run(**run_options)`.

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
python mcp_server.py   # default: stdio
```

### 2) Adding Tools (Generator)

```bash
vfmcp generate tool Search
```

This generates:

```
mcp_app/tools/search.py
tests/test_search.py
```

Implement your business logic in `mcp_app/tools/search.py`:

```python
# mcp_app/tools/search.py (example)
class SearchTool:
    """Business logic for 'search'."""
    async def run(self, params: dict):
        query = (params or {}).get("query")
        if not query:
            raise ValueError("missing 'query'")
        # TODO: implementation
        return {"results": [f"you searched: {query}"]}

### 3) Publishing to MCP (Auto-registration or Manual)

`mcp_server.py` contains this marker:

```python
# AUTO-REGISTER MARKER (do not remove): {VFMCP-AUTO-REGISTER}
```

When running `vfmcp generate tool <Name>`, the `@mcp.tool` function is **automatically added** after this marker (if CLI supports it).

For manual registration, add the following to `mcp_server.py`:

```python
from mcp_app.tools.search import SearchTool

@mcp.tool(name="search")
async def search(**kwargs):
    return await SearchTool().run(kwargs)
```

### 4) Testing

```bash
pytest -q
```

Example:

```python
# tests/test_search.py example
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

### 5) Client Usage

* **stdio**: Set `python mcp_server.py` as the "launch command" in Claude Desktop / MCP Inspector
* **http**: Change `run_options.transport=http` and set `http://host:port/path` in MCP client's remote connection

### 6) MCP Client Configuration

#### Configuration in Cursor

Create or edit the `.cursor/mcp.json` file to add your created MCP server:

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

**For stdio mode (recommended):**
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

**For http mode:**
```json
{
  "mcpServers": {
    "my-mcp-server": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

#### Other MCP Clients

- **Claude Desktop**: Add MCP server in settings
- **MCP Inspector**: Specify launch command or URL
- **VS Code**: Add server in MCP extension settings

**Note**: The `cwd` (current working directory) should point to the MCP server project root directory.

#### Running MCP Server in Docker Container

**stdio mode (via Docker):**
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

**http mode (via Docker):**
```json
{
  "mcpServers": {
    "my-mcp-docker": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

**Docker build and run:**
```bash
# Build image
docker build -t my-mcp-server .

# Start container (stdio mode)
docker run --rm -i my-mcp-server:latest

# Start container (http mode)
docker run --rm -p 8000:8000 my-mcp-server:latest
```

## Commands

### `new <dir> [--force]`

* Expands `templates/mcp/` into `<dir>`.
* Errors if `<dir>` contains files unless `--force` is given.

### `generate tool <Name> [--force]`

* Generates from `templates/tool/*.j2`:
  * `mcp_app/tools/<name>.py`
  * `tests/test_<name>.py`
* Fails if files exist unless `--force` is specified.

## Project Layout

```
veryfastmcp/
  __init__.py
  __main__.py            # python -m veryfastmcp entry
  cli.py                 # argparse-based CLI
  templates/
    mcp/                 # MCP server skeleton
      __init__.py
      __main__.py
      mcp_server.py
      configs/server.yaml
      mcp_app/...
      tests/...
    tool/                # generator templates
      tool.py.j2
      test_tool.py.j2
scripts/
  (none)
tests/
  test_cli.py            # subprocess tests for CLI
pyproject.toml
README.md
```

## License

MIT