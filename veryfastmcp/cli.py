"""Very Fast MCP CLI."""

import argparse
import re
import shutil
from importlib import resources
from pathlib import Path
from typing import Any


def _to_snake(name: str) -> str:
    """Convert ``Name`` to ``snake_case``."""
    name = re.sub(r"[^a-zA-Z0-9]+", "_", name)
    name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    return name.lower().strip("_")


def _class_base(name: str) -> str:
    """Return class-style ``CamelCase`` base from arbitrary input."""
    s = _to_snake(name)
    return "".join(p.title() for p in s.split("_"))


AUTO_REGISTER_MARKER = "# AUTO-REGISTER MARKER (do not remove): {VFMCP-AUTO-REGISTER}"


def update_server_registration(server_path: Path, tool_name: str, class_base: str) -> bool:
    """Insert an ``@mcp.tool`` registration block after the marker.

    Returns ``True`` if the file was modified, ``False`` otherwise.
    """
    if not server_path.exists():
        print(f"[WARN] {server_path} not found. Skipped MCP auto-registration.")
        return False

    text = server_path.read_text(encoding="utf-8")

    # Skip if tool already appears to be registered
    if f'@mcp.tool(name="{tool_name}")' in text or f"def {tool_name}(" in text:
        print(f"[INFO] Tool '{tool_name}' already registered in {server_path}.")
        return False

    idx = text.find(AUTO_REGISTER_MARKER)
    if idx == -1:
        print(f"[WARN] AUTO-REGISTER marker not found in {server_path}.")
        return False

    glue = f"""

# --- auto-registered by vfmcp ---
from mcp_app.tools.{tool_name} import {class_base}Tool

@mcp.tool(name="{tool_name}")
async def {tool_name}(**kwargs):
    return await {class_base}Tool().run(kwargs)
"""

    new_text = text.replace(AUTO_REGISTER_MARKER, AUTO_REGISTER_MARKER + glue)
    server_path.write_text(new_text, encoding="utf-8")
    print(f"[OK] Updated MCP server registration in {server_path}")
    return True

def _copy_pkg_dir(src_pkg: str, dst: Path) -> None:
    """Recursively copy a package directory to ``dst``."""
    root = resources.files(src_pkg)

    def _copy(node: Any, out: Path) -> None:
        if node.is_dir():
            out.mkdir(parents=True, exist_ok=True)
            for child in node.iterdir():
                _copy(child, out / child.name)
        else:
            out.parent.mkdir(parents=True, exist_ok=True)
            with resources.as_file(node) as f:
                shutil.copy2(f, out)

    _copy(root, dst)


def materialize_app_template(target: Path) -> None:
    """Copy app template and rename dotfiles."""
    _copy_pkg_dir("veryfastmcp.templates.app", target)

    gi_src = target / "gitignore"
    gi_dst = target / ".gitignore"
    if gi_src.exists():
        if gi_dst.exists():
            gi_dst.unlink()
        gi_src.rename(gi_dst)

def _render_and_write(target_dir: Path, template_path: Path, replacements: dict[str, str]) -> None:
    """Render a template file with replacements and write to target_dir."""
    with resources.as_file(template_path) as template_file:
        content = template_file.read_text(encoding="utf-8")
    for key, value in replacements.items():
        content = content.replace(f"{{{{ {key} }}}}", value)
    (target_dir / template_path.name).write_text(content, encoding="utf-8")


def cmd_new(args: argparse.Namespace) -> None:
    """Handle the ``new`` command."""
    target = Path(args.dir)
    project_name = target.name # プロジェクト名を取得

    if target.exists() and any(target.iterdir()) and not args.force:
        print(f"[ERROR] {target} is not empty. Use --force to overwrite.")
        raise SystemExit(1)

    target.mkdir(parents=True, exist_ok=True)

    _copy_pkg_dir("veryfastmcp.templates.mcp", target)
    materialize_app_template(target)

    replacements = {"project_name": project_name}

    # Render templates with project name
    _render_and_write(target, resources.files("veryfastmcp.templates.mcp") / "mcp_server.py", replacements)
    _render_and_write(target, resources.files("veryfastmcp.templates.mcp") / "pyproject.toml", replacements)
    _render_and_write(target, resources.files("veryfastmcp.templates.app") / "docker-compose.yml", replacements)
    _render_and_write(target, resources.files("veryfastmcp.templates.app") / "Dockerfile", replacements)

    # Copy test client script to project root
    test_client_src = resources.files("veryfastmcp.templates.mcp") / "test_client_stdio.py"
    test_client_dst = target / "test_client_stdio.py"
    if test_client_src.exists():
        with resources.as_file(test_client_src) as f:
            shutil.copy2(f, test_client_dst)
    test_client_src = resources.files("veryfastmcp.templates.mcp") / "test_client_http.py"
    test_client_dst = target / "test_client_http.py"
    if test_client_src.exists():
        with resources.as_file(test_client_src) as f:
            shutil.copy2(f, test_client_dst)


    # Copy both implementation guides
    impl_ja_src = resources.files("veryfastmcp.templates.mcp") / "IMPLEMENTATION.ja.md"
    impl_en_src = resources.files("veryfastmcp.templates.mcp") / "IMPLEMENTATION.md"
    
    if impl_ja_src.exists():
        with resources.as_file(impl_ja_src) as f:
            shutil.copy2(f, target / "IMPLEMENTATION.ja.md")
    
    if impl_en_src.exists():
        with resources.as_file(impl_en_src) as f:
            shutil.copy2(f, target / "IMPLEMENTATION.md")

    print(f"Created skeleton in {target}")


def cmd_generate_tool(args: argparse.Namespace) -> None:
    """Generate a tool and its accompanying test file."""
    tool_name = _to_snake(args.name)
    class_base = _class_base(args.name)
    tdir = resources.files("veryfastmcp.templates.tool")

    def render(p: Path) -> str:
        text = p.read_text(encoding="utf-8")
        return text.replace("{{ tool_name }}", tool_name).replace(
            "{{ class_base }}", class_base
        )

    tool_code = render(tdir / "tool.py")
    test_code = render(tdir / "test_tool.py")

    tool_path = Path("mcp_app/tools") / f"{tool_name}.py"
    test_path = Path("tests") / f"test_{tool_name}.py"

    if not args.force and (tool_path.exists() or test_path.exists()):
        print("[ERROR] generated files already exist. Use --force to overwrite.")
        raise SystemExit(1)

    tool_path.parent.mkdir(parents=True, exist_ok=True)
    test_path.parent.mkdir(parents=True, exist_ok=True)

    tool_path.write_text(tool_code, encoding="utf-8")
    test_path.write_text(test_code, encoding="utf-8")

    print(f"Generated: {tool_path} and {test_path}")

    server_file = Path("mcp_server.py")
    try:
        updated = update_server_registration(server_file, tool_name, class_base)
        if not updated:
            print(
                "[INFO] No server update performed (marker missing or already registered)."
            )
    except Exception as e:  # pragma: no cover - defensive
        print(f"[WARN] Failed to auto-register tool in {server_file}: {e}")


def main(argv: list[str] | None = None) -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="vfmcp", description="Very Fast MCP CLI"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_new = sub.add_parser("new", help="Create MCP server project skeleton")
    p_new.add_argument("dir")
    p_new.add_argument("--force", action="store_true")
    p_new.set_defaults(func=cmd_new)

    p_gen = sub.add_parser("generate", help="Code generators")
    gen_sub = p_gen.add_subparsers(dest="kind", required=True)
    p_tool = gen_sub.add_parser("tool", help="Generate a tool and its test")
    p_tool.add_argument("name")
    p_tool.add_argument("--force", action="store_true")
    p_tool.set_defaults(func=cmd_generate_tool)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()

