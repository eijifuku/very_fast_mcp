import asyncio
from mcp_app.tools.{{ tool_name }} import {{ class_base }}Tool


def test_{{ tool_name }}():
    tool = {{ class_base }}Tool()
    result = asyncio.run(tool.run({"query": "hello"}))
    assert result["results"] == ["example"]
