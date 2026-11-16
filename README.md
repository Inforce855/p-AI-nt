# p-AI-nt

An AI-native painting application with MCP-controlled artwork creation and a live human viewer.

**v0.1 — The Apprentice Edition** (initial development version)

The artist makes decisions; the application handles the drawing. No GIMP, Krita, Python scripting by the agent, or embedded AI model.

## Install on Nobara Linux

```bash
git clone https://github.com/Inforce855/p-AI-nt.git
cd p-AI-nt
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest -v test_engine
```

## Connect OpenChamber

Add a local stdio MCP server named `paint`. Use the absolute path of your clone. Example JSON for OpenChamber's MCP import (adjust paths):

```json
{
  "mcpServers": {
    "paint": {
      "command": "/home/tim/Projects/p-AI-nt/.venv/bin/python",
      "args": ["/home/tim/Projects/p-AI-nt/paint_server.py"]
    }
  }
}
```

The MCP process starts the viewer automatically. Open **http://127.0.0.1:8765** in your browser after the MCP server connects. No second process or document transfer required. Do not run multiple instances on the same port. Disable unrelated painting MCP servers for the test if desired, without deleting their configuration.

The server is local-only, and the viewer has no drawing endpoints. Any MCP client with access can modify the shared in-memory canvas. The optional PAINT_PORT environment variable changes the viewer port; PAINT_OUTPUT changes the artwork directory. Defaults: port 8765, artwork/ in the repository.

## Tools

| Tool | Purpose |
|---|---|
| new_canvas | Create a canvas with a coloured background |
| get_scene | Read dimensions and named layers, bottom to top |
| create_layer | Transparent canvas-sized top layer |
| paint | Filled ellipse, rectangle, polygon; continuous stroke, cubic curve or erase |
| paint_batch | Up to 256 marks on one layer in one undoable operation |
| layer_control | Set visibility, opacity and stack position |
| look | Actual PNG image for visual feedback |
| undo | Undo last change |
| save | Save composite PNG plus layered .paint archive |

Coordinates: canvas pixels from top-left. Ellipse and rectangle use two points (top-left, bottom-right). Polygon uses vertices. Stroke and erase use path points. Curve uses start, two cubic controls, end. Colour is CSS or hex, opacity is 0–1, width is pixels. All operations use explicit named layers; no hidden active brush.

Example paint arguments: {"layer":"Ears","kind":"polygon","points":[[20,80],[50,20],[80,80]],"color":"#FF9633"}.

## First benchmark

Use Gemma E4B, a fresh session, and only this prompt:

> Paint a cartoon orange tabby cat with green eyes, pointed ears, pink inner ears and a pale blue background.

Observe time to first mark, tool errors, recognisability, layers and whether the model inspects and corrects the artwork. No supplied coordinates or technical instructions. Compare Gemma 26B and 31B using the same prompt later.

## Current limitations

This is an initial implementation, not a validated release. Hard-edged raster marks with basic rounded strokes and cubic curves; no natural-media texture yet. Live viewer refreshes after each operation/batch. Undo retains up to 20 snapshots with a memory budget. Single in-memory document; save before disconnecting. Layered archives contain scene metadata and PNG layers, but reopening is not yet implemented. Region snapshots, reference-image import and native desktop packaging are deferred.

See [PROJECT_STATUS.md](PROJECT_STATUS.md) for progress and next actions.

MIT licence.
