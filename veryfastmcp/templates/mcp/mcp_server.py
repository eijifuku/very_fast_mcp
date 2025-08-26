from fastmcp import FastMCP
from pathlib import Path
import sys

try:
    import yaml
except Exception:
    print("[ERROR] PyYAML is required. Please `pip install -e .[mcp]`.", file=sys.stderr)
    raise

from mcp_app.tools.greet import GreetTool

# Import additional tools here as needed
# from mcp_app.tools.example import ExampleTool

mcp = FastMCP("veryfastmcp-mcp")

# AUTO-REGISTER MARKER (do not remove): {VFMCP-AUTO-REGISTER}

@mcp.tool(name="greet")
async def greet(name: str) -> str:
    out = await GreetTool().run({"name": name})
    return out["message"] if isinstance(out, dict) else getattr(out, "message", str(out))

def load_run_options(path: str = "configs/server.yaml") -> dict:
    p = Path(path)
    if not p.exists():
        return {"transport": "stdio"}  # 既定値
    data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    opts = data.get("run_options") or {}
    opts.setdefault("transport", "stdio")
    return opts

if __name__ == "__main__":
    run_options = load_run_options()
    # 設定をそのまま FastMCP.run に渡す
    mcp.run(**run_options)
