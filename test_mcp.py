"""Integration smoke test against an already running local studio.
Run on a fresh studio: creates one layer, paints a mark, then undoes both.
"""
import asyncio
import base64
import io
import os
import uuid

import httpx
from PIL import Image
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

BASE = "http://127.0.0.1:" + os.environ.get("PAINT_PORT", "8765")


async def main():
    name = "Smoke test " + uuid.uuid4().hex[:8]
    async with httpx.AsyncClient() as http:
        initial = (await http.get(BASE + "/state")).json()
        async with streamablehttp_client(BASE + "/mcp") as (r1, w1, _):
            async with ClientSession(r1, w1) as a:
                await a.initialize()
                tools = await a.list_tools()
                assert len(tools.tools) == 9, [t.name for t in tools.tools]
                scene = await a.call_tool("get_scene", {})
                assert not scene.isError, scene
                created = await a.call_tool("create_layer", {"name": name})
                assert not created.isError, created
                try:
                    async with streamablehttp_client(BASE + "/mcp") as (r2, w2, _):
                        async with ClientSession(r2, w2) as b:
                            await b.initialize()
                            result = await b.call_tool("paint", {
                                "layer": name, "kind": "rectangle",
                                "points": [[0, 0], [20, 20]], "color": "#FF9633"})
                            assert not result.isError, result
                            try:
                                state = (await http.get(BASE + "/state")).json()
                                assert state["revision"] == initial["revision"] + 2, state
                                assert state["layers"][-1]["name"] == name, state
                                snap = await a.call_tool("look", {"max_size": 768})
                                assert not snap.isError, snap
                                images = [c for c in snap.content if c.type == "image"]
                                assert images, snap
                                with Image.open(io.BytesIO(base64.b64decode(images[0].data))) as img:
                                    assert img.convert("RGBA").getpixel((0, 0)) == (255,150,51,255)
                                png = await http.get(BASE + "/canvas.png")
                                png.raise_for_status()
                                with Image.open(io.BytesIO(png.content)) as img:
                                    assert img.convert("RGBA").getpixel((0, 0)) == (255,150,51,255)
                            finally:
                                undone = await b.call_tool("undo", {})
                                assert not undone.isError, undone
                finally:
                    undone = await a.call_tool("undo", {})
                    assert not undone.isError, undone
        final = (await http.get(BASE + "/state")).json()
        assert final["layers"] == initial["layers"], final
    print("PASS: nine tools, two MCP connections, shared canvas, PNG feedback, viewer and undo")


if __name__ == "__main__":
    asyncio.run(main())
