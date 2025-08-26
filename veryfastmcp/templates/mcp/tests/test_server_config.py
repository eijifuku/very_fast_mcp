from mcp_server import load_run_options
from pathlib import Path

def test_default_stdio(tmp_path: Path):
    cfg = load_run_options(path=str(tmp_path / "missing.yaml"))
    assert cfg == {"transport": "stdio"}

def test_http_options(tmp_path: Path):
    y = tmp_path / "server.yaml"
    y.write_text(
        "run_options:\n  transport: http\n  host: 0.0.0.0\n  port: 9001\n  path: /mcp\n",
        encoding="utf-8",
    )
    cfg = load_run_options(path=str(y))
    assert cfg["transport"] == "http"
    assert cfg["host"] == "0.0.0.0"
    assert cfg["port"] == 9001
    assert cfg["path"] == "/mcp"
