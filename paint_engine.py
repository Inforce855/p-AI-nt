"""Deterministic, layered raster painting. No GUI or model dependency."""
from __future__ import annotations

import io
import json
import math
import re
import threading
import zipfile
from pathlib import Path

from PIL import Image, ImageColor, ImageDraw, ImageChops


def colour(value: str) -> tuple[int, int, int, int]:
    if not isinstance(value, str):
        raise ValueError("Use a CSS colour or #RRGGBB.")
    return ImageColor.getcolor(value, "RGBA")


class Studio:
    def __init__(self):
        self.lock = threading.RLock()
        self.width = self.height = 512
        self.title = "Untitled"
        self.layers = []
        self.history = []
        self.revision = 0
        self.last_action = "Ready"
        self.new_canvas(512, 512, "#FFFFFF", "Untitled")

    def _layer(self, name):
        for layer in self.layers:
            if layer["name"] == name:
                return layer
        raise ValueError(f"Layer {name!r} not found. Available: {[l['name'] for l in self.layers]}")

    def _remember(self):
        self.history.append((self.width, self.height, self.title,
                             [{**l, "image": l["image"].copy()} for l in self.layers]))
        # Bound snapshot history by approximate raster bytes.
        def size(state):
            return state[0] * state[1] * 4 * len(state[3])
        while len(self.history) > 20 or (len(self.history) > 1 and
                sum(size(s) for s in self.history) > 128 * 1024 * 1024):
            self.history.pop(0)

    def _changed(self, action):
        self.revision += 1
        self.last_action = action

    def new_canvas(self, width=512, height=512, background="#FFFFFF", title="Untitled"):
        with self.lock:
            if type(width) is not int or type(height) is not int or not (1 <= width <= 2048 and 1 <= height <= 2048):
                raise ValueError("Canvas dimensions must be integers from 1 to 2048.")
            if not isinstance(title, str) or not title.strip() or len(title) > 120:
                raise ValueError("Title must be 1–120 characters.")
            image = Image.new("RGBA", (width, height), colour(background))
            if self.layers:
                self._remember()
            self.width, self.height, self.title = width, height, title
            self.layers = [{"name": "Background", "visible": True, "opacity": 1.0, "image": image}]
            self._changed("New canvas")
            return self.scene()

    def scene(self):
        with self.lock:
            return {"title": self.title, "width": self.width, "height": self.height,
                    "revision": self.revision, "last_action": self.last_action,
                    "undo_available": len(self.history),
                    "layers": [{k: v for k, v in l.items() if k != "image"} for l in self.layers],
                    "layer_order": "bottom to top"}

    def create_layer(self, name):
        with self.lock:
            if not isinstance(name, str) or not name.strip() or len(name) > 80:
                raise ValueError("Layer name must be 1–80 characters.")
            if any(l["name"] == name for l in self.layers):
                raise ValueError(f"Layer {name!r} already exists. Paint on it directly.")
            if len(self.layers) >= 24:
                raise ValueError("Maximum 24 layers.")
            image = Image.new("RGBA", (self.width, self.height))
            self._remember()
            self.layers.append({"name": name, "visible": True, "opacity": 1.0, "image": image})
            self._changed(f"Created layer {name}")
            return {"layer": name, "position": "top", "transparent": True, "revision": self.revision}

    def layer_control(self, name, visible=None, opacity=None, position=None):
        with self.lock:
            layer = self._layer(name)
            if opacity is not None and not 0 <= opacity <= 1:
                raise ValueError("Opacity must be 0–1.")
            if position is not None and (type(position) is not int or not 0 <= position < len(self.layers)):
                raise ValueError("Position is a zero-based index, 0 = bottom.")
            if visible is not None and type(visible) is not bool:
                raise ValueError("Visible must be true or false.")
            self._remember()
            if visible is not None:
                layer["visible"] = visible
            if opacity is not None:
                layer["opacity"] = opacity
            if position is not None:
                self.layers.remove(layer)
                self.layers.insert(position, layer)
            self._changed(f"Updated layer {name}")
            return self.scene()

    def _draw(self, target, op):
        kind = op.get("kind")
        points = op.get("points")
        if not isinstance(points, list) or not 1 <= len(points) <= 4096:
            raise ValueError("points must contain 1–4096 [x,y] pairs.")
        xy = []
        for p in points:
            if not isinstance(p, (list, tuple)) or len(p) != 2 or any(
                type(n) not in (int, float) or not math.isfinite(n) or abs(n) > 8192 for n in p
            ):
                raise ValueError("Every point must be a finite [x,y] pair within ±8192.")
            xy.append(tuple(p))
        opacity = op.get("opacity", 1.0)
        width = op.get("width", 4)
        if type(opacity) not in (int, float) or not 0 <= opacity <= 1:
            raise ValueError("Opacity must be 0–1.")
        if type(width) not in (int, float) or not 1 <= width <= 512:
            raise ValueError("Width must be 1–512 pixels.")
        rgba = colour(op.get("color", "#000000"))
        rgba = (*rgba[:3], round(rgba[3] * opacity))
        overlay = Image.new("RGBA", target.size)
        draw = ImageDraw.Draw(overlay)
        if kind in ("ellipse", "rectangle"):
            if len(xy) != 2 or xy[0][0] >= xy[1][0] or xy[0][1] >= xy[1][1]:
                raise ValueError("Ellipse/rectangle needs two points: top-left and bottom-right.")
            box = [*xy[0], *xy[1]]
            (draw.ellipse if kind == "ellipse" else draw.rectangle)(box, fill=rgba)
        elif kind == "polygon":
            if len(xy) < 3:
                raise ValueError("Polygon needs at least three points.")
            draw.polygon(xy, fill=rgba)
        elif kind in ("stroke", "curve", "erase"):
            if kind == "curve":
                if len(xy) != 4:
                    raise ValueError("Curve needs four points: start, control 1, control 2, end.")
                a, b, c, d = xy
                xy = [tuple((1-t)**3*a[j]+3*(1-t)**2*t*b[j]+3*(1-t)*t*t*c[j]+t**3*d[j]
                            for j in (0, 1)) for t in (i/96 for i in range(97))]
            w = round(width)
            if kind == "erase":
                rgba = (255, 255, 255, round(255 * opacity))
            if len(xy) > 1:
                draw.line(xy, fill=rgba, width=w, joint="curve")
            for x, y in (xy[0], xy[-1]):
                radius = w / 2
                draw.ellipse((x-radius, y-radius, x+radius, y+radius), fill=rgba)
        else:
            raise ValueError("kind must be ellipse, rectangle, polygon, stroke, curve or erase.")
        if kind == "erase":
            target.putalpha(ImageChops.multiply(target.getchannel("A"),
                                                  ImageChops.invert(overlay.getchannel("A"))))
        else:
            target.alpha_composite(overlay)

    def paint(self, layer, operations):
        with self.lock:
            if not isinstance(operations, list) or not 1 <= len(operations) <= 256:
                raise ValueError("Batch must contain 1–256 operations.")
            dest = self._layer(layer)
            # Validate and draw on a copy: a bad batch cannot partially change the painting.
            scratch = dest["image"].copy()
            for i, op in enumerate(operations):
                try:
                    self._draw(scratch, op)
                except (ValueError, TypeError, AttributeError) as exc:
                    raise ValueError(f"Operation {i + 1}: {exc}") from exc
            changed = ImageChops.difference(dest["image"], scratch)
            bounds = changed.getbbox(alpha_only=False)
            if bounds is None:
                return {"layer": layer, "operations": len(operations), "changed": False,
                        "revision": self.revision}
            self._remember()
            dest["image"] = scratch
            self._changed(f"Painted {len(operations)} operation(s) on {layer}")
            return {"layer": layer, "operations": len(operations), "changed": True,
                    "bounds": list(bounds), "revision": self.revision}

    def composite(self):
        with self.lock:
            result = Image.new("RGBA", (self.width, self.height))
            for l in self.layers:
                if not l["visible"]:
                    continue
                image = l["image"]
                if l["opacity"] != 1:
                    image = image.copy()
                    image.putalpha(image.getchannel("A").point(lambda x: round(x*l["opacity"])))
                result.alpha_composite(image)
            return result

    def png(self, max_size=None):
        image = self.composite()
        if max_size is not None:
            if type(max_size) is not int or not 64 <= max_size <= 2048:
                raise ValueError("max_size must be 64–2048.")
            image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return buffer.getvalue()

    def undo(self):
        with self.lock:
            if not self.history:
                return {"changed": False, "revision": self.revision}
            self.width, self.height, self.title, self.layers = self.history.pop()
            self._changed("Undo")
            return self.scene()

    def save(self, directory, name):
        if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9 _-]{0,79}", name):
            raise ValueError("Use a simple filename without an extension or path.")
        with self.lock:
            directory = Path(directory)
            directory.mkdir(parents=True, exist_ok=True)
            png = directory / (name + ".png")
            project = directory / (name + ".paint")
            if png.exists() or project.exists():
                raise ValueError("That artwork name already exists. Choose a new name.")
            # Both outputs use exclusive creation; never overwrite existing work.
            with project.open("xb") as f:
                with zipfile.ZipFile(f, "w", zipfile.ZIP_DEFLATED) as archive:
                    archive.writestr("scene.json", json.dumps(self.scene(), indent=2))
                    for i, l in enumerate(self.layers):
                        buffer = io.BytesIO()
                        l["image"].save(buffer, format="PNG")
                        archive.writestr(f"layers/{i}.png", buffer.getvalue())
            with png.open("xb") as f:
                f.write(self.png())
            return {"png": str(png), "project": str(project), "revision": self.revision}
