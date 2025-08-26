import asyncio
from mcp_app.tools.greet import GreetTool


def test_greet():
    tool = GreetTool()
    result = asyncio.run(tool.run({"name": "World"}))
    assert result["message"] == "Hello, World!"
