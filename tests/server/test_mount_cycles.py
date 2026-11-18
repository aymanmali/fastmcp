import pytest

from fastmcp import Client, FastMCP
from fastmcp.server.providers import FastMCPProvider
from fastmcp.server.providers.aggregate import AggregateProvider


def test_direct_self_mount_rejected():
    a = FastMCP("A")
    with pytest.raises(ValueError, match="Cannot mount a server onto itself"):
        a.mount(a)


def test_two_server_mount_cycle_rejected():
    a = FastMCP("A")
    b = FastMCP("B")
    a.mount(b, "b")
    with pytest.raises(ValueError, match="mount cycle"):
        b.mount(a, "a")


def test_three_server_mount_cycle_rejected():
    a = FastMCP("A")
    b = FastMCP("B")
    c = FastMCP("C")
    a.mount(b, "b")
    b.mount(c, "c")
    with pytest.raises(ValueError, match="mount cycle"):
        c.mount(a, "a")


async def test_acyclic_diamond_mount_allowed():
    a = FastMCP("A")
    b = FastMCP("B")
    c = FastMCP("C")
    d = FastMCP("D")

    @d.tool
    def ping() -> str:
        return "pong"

    b.mount(d, "d")
    c.mount(d, "d")
    a.mount(b, "b")
    a.mount(c, "c")

    async with Client(a) as client:
        tools = await client.list_tools()
        assert {t.name for t in tools} == {"b_d_ping", "c_d_ping"}


def test_add_provider_cycle_rejected():
    a = FastMCP("A")
    b = FastMCP("B")
    a.mount(b)
    with pytest.raises(ValueError, match="mount cycle"):
        b.add_provider(FastMCPProvider(a))


def test_raw_fastmcp_inside_aggregate_provider_cycle_rejected():
    a = FastMCP("A")
    b = FastMCP("B", providers=[AggregateProvider([a])])
    with pytest.raises(ValueError, match="mount cycle"):
        a.mount(b)
