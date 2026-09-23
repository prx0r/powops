"""MCP integration test — smoke test for powops MCP server.

Starts the MCP server over stdio, performs initialize handshake,
lists tools, and verifies the response.
"""

import asyncio
import json
import subprocess
import sys
import os

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


async def _run_mcp_test():
    """Run MCP server and test initialize + list_tools."""
    proc = await asyncio.create_subprocess_exec(
        sys.executable, "-m", "powops.mcp",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=ROOT,
    )

    try:
        # Send initialize
        init_msg = json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test", "version": "0.1"},
            },
        }) + "\n"

        proc.stdin.write(init_msg.encode())
        await proc.stdin.drain()

        # Read initialize response
        line = await asyncio.wait_for(proc.stdout.readline(), timeout=10)
        resp = json.loads(line)
        assert resp["id"] == 1
        assert "result" in resp
        assert resp["result"]["serverInfo"]["name"] == "powops"

        # Send tools/list
        list_msg = json.dumps({
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {},
        }) + "\n"

        proc.stdin.write(list_msg.encode())
        await proc.stdin.drain()

        # Read tools/list response
        line = await asyncio.wait_for(proc.stdout.readline(), timeout=10)
        resp = json.loads(line)
        assert resp["id"] == 2
        assert "result" in resp
        tools = resp["result"]["tools"]
        tool_names = [t["name"] for t in tools]

        # Verify expected tools exist
        expected = ["powops_status", "powops_source", "powops_history",
                    "powops_uptime", "powops_incidents", "powops_coverage",
                    "powops_schemas", "powops_verify", "powops_sources",
                    "powops_events"]
        for name in expected:
            assert name in tool_names, f"missing tool: {name}"

        return True

    except Exception as e:
        print(f"MCP test failed: {e}")
        return False

    finally:
        proc.terminate()
        try:
            await asyncio.wait_for(proc.wait(), timeout=2)
        except asyncio.TimeoutError:
            proc.kill()


def test_mcp_initialize_and_list_tools():
    """Test MCP server initializes and lists tools."""
    result = asyncio.run(_run_mcp_test())
    assert result, "MCP integration test failed"


if __name__ == "__main__":
    result = asyncio.run(_run_mcp_test())
    print("PASS" if result else "FAIL")
    sys.exit(0 if result else 1)
