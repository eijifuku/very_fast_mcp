"""Tests for the CLI."""

import os
import subprocess
import sys
from pathlib import Path


def run_cli(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.setdefault("PYTHONPATH", str(Path(__file__).resolve().parents[1]))
    return subprocess.run(
        [sys.executable, "-m", "veryfastmcp.cli", *args],
        cwd=cwd,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )


def test_new(tmp_path: Path) -> None:
    project = tmp_path / "my-app"
    result = run_cli("new", str(project))
    assert result.returncode == 0
    assert (project / "mcp_server.py").exists()
    assert (project / "configs/server.yaml").exists()
    # Dockerfile templates
    assert (project / "Dockerfile").exists()
    assert not (project / "Dockerfile.stdio").exists()
    assert not (project / "Dockerfile.http").exists()
    assert (project / ".dockerignore").exists()
    assert (project / ".gitignore").exists()
    
    # Check unified Dockerfile content
    df = (project / "Dockerfile").read_text(encoding="utf-8")
    assert 'CMD ["python", "mcp_server.py"]' in df
    assert "# EXPOSE 8009" in df
    assert '# CMD ["python", "mcp_server.py", "--transport", "http"' in df


def test_generate_tool(tmp_path: Path) -> None:
    project = tmp_path / "my-app"
    run_cli("new", str(project))
    result = run_cli("generate", "tool", "Search", cwd=project)
    assert result.returncode == 0
    assert (project / "mcp_app/tools/search.py").exists()
    assert (project / "tests/test_search.py").exists()
    server_text = (project / "mcp_server.py").read_text(encoding="utf-8")
    assert "from mcp_app.tools.search import SearchTool" in server_text
    assert "@mcp.tool(name=\"search\")" in server_text
