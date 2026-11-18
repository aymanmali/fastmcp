from fastmcp import FastMCP
from fastmcp.server.providers import LocalProvider
from fastmcp.server.providers.aggregate import AggregateProvider
from fastmcp.server.transforms import Namespace


async def test_aggregate_provider_get_tasks_applies_transforms():
    local = LocalProvider()

    @local.tool(task=True)
    async def square(n: int) -> int:
        return n * n

    aggregate = AggregateProvider([local])
    aggregate.add_transform(Namespace("math"))
    mcp = FastMCP("demo", providers=[aggregate])

    tool = await mcp.get_tool("math_square")
    assert tool is not None
    assert tool.key == "tool:math_square@"

    tasks = await mcp.get_tasks()
    assert [c.key for c in tasks] == ["tool:math_square@"]


async def test_fastmcp_server_namespace_transform_applied_once_in_get_tasks():
    mcp = FastMCP("demo")

    @mcp.tool(task=True)
    async def slow_thing() -> str:
        return "ok"

    mcp.add_transform(Namespace("api"))

    tool = await mcp.get_tool("api_slow_thing")
    assert tool is not None
    assert tool.key == "tool:api_slow_thing@"

    tasks = await mcp.get_tasks()
    assert [c.key for c in tasks] == ["tool:api_slow_thing@"]
