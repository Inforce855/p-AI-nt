"""p-AI-nt MCP stdio server and read-only local live viewer."""
from __future__ import annotations

import json
import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Literal
from urllib.parse import urlsplit

from mcp.server.fastmcp import FastMCP, Image
from pydantic import BaseModel, Field
from paint_engine import Studio

studio = Studio()
mcp = FastMCP("p-AI-nt", instructions="Paint directly with p-AI-nt tools. "
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


class Viewer(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        path = urlsplit(self.path).path
        if path == "/":
            body, mime = (ROOT / "viewer.html").read_bytes(), "text/html; charset=utf-8"
        elif path == "/state":
            body, mime = json.dumps(studio.scene()).encode(), "application/json"
        elif path == "/canvas.png":
            body, mime = studio.png(), "image/png"
        else:
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)


def main():
    port = int(os.environ.get("PAINT_PORT", "8765"))
    try:
        viewer = ThreadingHTTPServer(("127.0.0.1", port), Viewer)
    except OSError as exc:
        raise SystemExit(f"Cannot start p-AI-nt viewer on port {port}. Stop the other instance or choose PAINT_PORT: {exc}")
    thread = threading.Thread(target=viewer.serve_forever, daemon=True)
    thread.start()
    print(f"p-AI-nt viewer: http://127.0.0.1:{port}", file=sys.stderr)
    try:
        mcp.run(transport="stdio")
    finally:
        viewer.shutdown()
        viewer.server_close()


if __name__ == "__main__":
    main()
