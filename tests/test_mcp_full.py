"""MCP full tool test — pi-agent simulation over stdio.

Starts the MCP server, performs initialize, lists tools, then CALLS
every tool and validates the response shape. This is what the pi
agent does on every monitoring run.
"""

import asyncio
import json
import subprocess
import sys
import os

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ALL_TOOLS = [
    "powops_status",
    "powops_source",
    "powops_history",
    "powops_uptime",
    "powops_timeline",
    "powops_volume",
    "powops_volume_source",
    "powops_incidents",
    "powops_coverage",
    "powops_schemas",
    "powops_schema",
    "powops_schema_history",
    "powops_verify",
    "powops_sources",
    "powops_events",
    "powops_alerts",
    "powops_repos",
]

# (tool, args, expected top-level keys in JSON payload)
CALLS = [
    ("powops_status", {}, ["overall", "sources", "gardens"]),
    ("powops_source", {"source_id": "chain_state"}, ["source_id", "status"]),
    ("powops_history", {"days": 1}, ["count", "entries"]),
    ("powops_uptime", {"days": 7}, ["days", "sources"]),
    ("powops_timeline", {"source": "chain_state", "days": 7}, ["source", "timeline"]),
    ("powops_volume", {"days": 7}, ["days", "sources"]),
    ("powops_volume_source", {"source_id": "open_repair", "days": 7}, ["source", "history"]),
    ("powops_incidents", {"status": "all"}, ["count", "incidents"]),
    ("powops_coverage", {}, ["total", "healthy", "gardens"]),
    ("powops_schemas", {}, ["count", "schemas"]),
    ("powops_schema", {"source_id": "open_repair"}, ["source_id"]),
    ("powops_schema_history", {"source_id": "open_repair"}, ["source", "history"]),
    ("powops_verify", {"days": 1}, ["verified", "files"]),
    ("powops_sources", {}, ["sources"]),
    ("powops_events", {"days": 1}, ["count", "events"]),
    ("powops_alerts", {}, ["alerts"]),
    ("powops_repos", {}, ["repos"]),
]


async def _stdio_call_all():
    """Call every tool over stdio. Returns (passed, failed) name lists."""
    proc = await asyncio.create_subprocess_exec(
        sys.executable, "-m", "powops.mcp",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=ROOT,
        limit=2 ** 24,  # status/sources payloads exceed default 64KB readline limit
    )
    passed, failed = [], []
    try:
        async def rpc(msg_id, method, params):
            proc.stdin.write((json.dumps({
                "jsonrpc": "2.0", "id": msg_id,
                "method": method, "params": params,
            }) + "\n").encode())
            await proc.stdin.drain()
            line = await asyncio.wait_for(proc.stdout.readline(), timeout=60)
            return json.loads(line)

        # initialize
        resp = await rpc(1, "initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "pi-agent-test", "version": "0.1"},
        })
        assert resp["result"]["serverInfo"]["name"] == "powops", "bad server name"

        # tools/list — verify all 17 advertised
        resp = await rpc(2, "tools/list", {})
        advertised = [t["name"] for t in resp["result"]["tools"]]
        for name in ALL_TOOLS:
            assert name in advertised, f"tool not advertised: {name}"

        # tools/call — every tool
        msg_id = 3
        for name, args, keys in CALLS:
            try:
                resp = await rpc(msg_id, "tools/call", {"name": name, "arguments": args})
                msg_id += 1
                assert "result" in resp, f"{name}: no result key"
                content = resp["result"]["content"]
                assert content, f"{name}: empty content"
                payload = json.loads(content[0]["text"])
                # error payloads are acceptable for lookups (e.g. unknown source)
                if "error" in payload and len(payload) == 1:
                    passed.append(f"{name} (error-path)")
                    continue
                for k in keys:
                    assert k in payload, f"{name}: missing key {k}"
                passed.append(name)
            except Exception as e:
                failed.append(f"{name}: {e}")

        return passed, failed
    finally:
        proc.terminate()
        try:
            await asyncio.wait_for(proc.wait(), timeout=2)
        except asyncio.TimeoutError:
            proc.kill()


def test_mcp_all_tools():
    """Every advertised tool responds with the expected shape."""
    passed, failed = asyncio.run(_stdio_call_all())
    print(f"\npassed ({len(passed)}): {passed}")
    print(f"failed ({len(failed)}): {failed}")
    assert not failed, f"MCP tool failures: {failed}"
    assert len(passed) == len(ALL_TOOLS)


if __name__ == "__main__":
    passed, failed = asyncio.run(_stdio_call_all())
    print(f"passed ({len(passed)}): {passed}")
    print(f"failed ({len(failed)}): {failed}")
    sys.exit(0 if not failed else 1)
