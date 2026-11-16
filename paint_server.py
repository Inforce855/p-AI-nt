"""One local p-AI-nt studio with Streamable HTTP MCP and a read-only viewer."""
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Literal

from mcp.server.fastmcp import FastMCP, Image
from pydantic import BaseModel, Field
from starlette.responses import FileResponse, JSONResponse, Response
from mcp.server.transport_security import TransportSecuritySettings
from paint_engine import Studio

PORT = int(os.environ.get("PAINT_PORT", "8765"))
studio = Studio()
mcp = FastMCP("p-AI-nt", host="127.0.0.1", port=PORT,
    stateless_http=True, json_response=True,
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=[f"127.0.0.1:{PORT}", f"localhost:{PORT}"],
        allowed_origins=[f"http://127.0.0.1:{PORT}", f"http://localhost:{PORT}"],
    ),
    instructions="Paint directly with p-AI-nt tools. "
    "Canvas coordinates are pixels from the top-left. Create transparent named layers, "
    "paint shapes or strokes, then look to inspect the result. No Python scripts needed.")
ROOT = Path(__file__).resolve().parent
OUTPUT = Path(os.environ.get("PAINT_OUTPUT", str(ROOT / "artwork"))).expanduser()


class Mark(BaseModel):
    kind: Literal["ellipse", "rectangle", "polygon", "stroke", "curve", "erase"]
    points: list[list[float]] = Field(description="Canvas [x,y] pairs. Ellipse/rectangle: top-left and bottom-right. Polygon: vertices. Stroke: path. Curve: start, two controls, end.")
    color: str = "#000000"
    width: float = 4
    opacity: float = 1.0


@mcp.tool()
def new_canvas(width: int = 512, height: int = 512, background: str = "#FFFFFF", title: str = "Untitled") -> dict:
    """Start a fresh painting, 1–2048 pixels per side. Background is a CSS/hex colour. Undo restores the previous canvas."""
    return studio.new_canvas(width, height, background, title)


@mcp.tool()
def get_scene() -> dict:
    """Read canvas size, named layers (bottom to top), revision and last action."""
    return studio.scene()


@mcp.tool()
def create_layer(name: str) -> dict:
    """Add a transparent canvas-sized layer above all existing layers. Name must be unique."""
    return studio.create_layer(name)


@mcp.tool()
def paint(layer: str, kind: Literal["ellipse", "rectangle", "polygon", "stroke", "curve", "erase"],
          points: list[list[float]], color: str = "#000000", width: float = 4, opacity: float = 1.0) -> dict:
    """Paint one mark on a named layer. Coordinates are canvas pixels from top-left.
    ellipse/rectangle: two points, top-left and bottom-right; filled.
    polygon: three or more vertices; filled. stroke: connected points with round ends.
    curve: four points, start, two cubic Bezier controls, end. erase: transparent stroke.
    color is #RRGGBB or CSS colour, width is pixels, opacity is 0–1.
    Example: kind=polygon, points=[[20,80],[50,20],[80,80]], color=#FF9633."""
    return studio.paint(layer, [dict(kind=kind, points=points, color=color, width=width, opacity=opacity)])


@mcp.tool()
def paint_batch(layer: str, marks: list[Mark]) -> dict:
    """Paint up to 256 marks on one layer in order. Same fields as paint. One undo reverses the whole batch."""
    return studio.paint(layer, [mark.model_dump() for mark in marks])


@mcp.tool()
def layer_control(name: str, visible: bool | None = None, opacity: float | None = None,
                  position: int | None = None) -> dict:
    """Change layer visibility, opacity (0–1), or order (0=bottom). Omitted fields stay unchanged."""
    return studio.layer_control(name, visible, opacity, position)


@mcp.tool()
def look(max_size: int = 768) -> Image:
    """See the actual current painting as a PNG. Use after painting to inspect and correct. max_size is preview pixels, 64–2048."""
    return Image(data=studio.png(max_size), format="png")


@mcp.tool()
def undo() -> dict:
    """Undo the most recent canvas, layer or painting change."""
    return studio.undo()


@mcp.tool()
def save(name: str = "Painting") -> dict:
    """Save composite PNG and layered .paint archive in the local artwork folder. Use a new simple name; never overwrites."""
    return studio.save(OUTPUT, name)


# Both the viewer and MCP share this single Studio instance.
# Only MCP exposes drawing operations. Browser routes are read-only.
HEADERS = {"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"}


@mcp.custom_route("/", methods=["GET"])
async def viewer(request):
    return FileResponse(ROOT / "viewer.html", media_type="text/html", headers=HEADERS)


@mcp.custom_route("/state", methods=["GET"])
async def viewer_state(request):
    return JSONResponse(studio.scene(), headers=HEADERS)


@mcp.custom_route("/canvas.png", methods=["GET"])
async def viewer_canvas(request):
    return Response(studio.png(), media_type="image/png", headers=HEADERS)


def main():
    print(f"p-AI-nt viewer: http://127.0.0.1:{PORT}", file=sys.stderr)
    print(f"p-AI-nt MCP: http://127.0.0.1:{PORT}/mcp", file=sys.stderr)
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
