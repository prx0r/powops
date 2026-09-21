"""MCP integration test — smoke test for powops MCP server.

Starts the MCP server over stdio, performs initialize handshake,
lists tools, invokes powops_status, and verifies the response.
"""

import asyncio
import json
import subprocess
import sys
import os

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


async def _run_mcp_test():
    """Run MCP server and test initialize + list_tools + call_tool."""
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
        line = await asyncio.wait_for(proc.stdout.readline(), timeout=5)
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
        line = await asyncio.wait_for(proc.stdout.readline(), timeout=5)
        resp = json.loads(line)
        assert resp["id"] == 2
        assert "result" in resp
        tools = resp["result"]["tools"]
        tool_names = [t["name"] for t in tools]
        assert "powops_status" in tool_names
        assert "powops_diagnose" in tool_names
        assert "powops_incidents" in tool_names
        assert "powops_coverage" in tool_names

        # Send tools/call for powops_status
        call_msg = json.dumps({
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "powops_status",
                "arguments": {},
            },
        }) + "\n"

        proc.stdin.write(call_msg.encode())
        await proc.stdin.drain()

        # Read tools/call response
        line = await asyncio.wait_for(proc.stdout.readline(), timeout=15)
        resp = json.loads(line)
        assert resp["id"] == 3
        assert "result" in resp
        content = resp["result"]["content"]
        assert len(content) > 0
        result_data = json.loads(content[0]["text"])
        assert "overall" in result_data
        assert "sources" in result_data
        assert isinstance(result_data["sources"], list)
        assert len(result_data["sources"]) > 0

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
    result = asyncio.get_event_loop().run_until_complete(_run_mcp_test())
    assert result, "MCP integration test failed"


if __name__ == "__main__":
    result = asyncio.get_event_loop().run_until_complete(_run_mcp_test())
    print("PASS" if result else "FAIL")
    sys.exit(0 if result else 1)
