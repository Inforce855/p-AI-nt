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

## Start the studio and connect OpenChamber

Start the application once, in a terminal:

```bash
cd ~/Projects/p-AI-nt
.venv/bin/python paint_server.py
```

Keep that terminal running. Open the live viewer at **http://127.0.0.1:8765**.

In OpenChamber, edit the existing MCP entry named `paint`. Choose **Link** rather than Command and enter **http://127.0.0.1:8765/mcp**. Connect. If editing the OpenCode configuration directly, preserve the rest of the configuration and set the existing paint entry to the following remote endpoint:

```json
{
  "type": "remote",
  "url": "http://127.0.0.1:8765/mcp",
  "enabled": true,
  "oauth": false
}
```

Here "remote" means HTTP transport, not an internet service: everything runs on your own machine. The studio binds to loopback only. Do not expose the unauthenticated local endpoint to the network. Multiple MCP connections use one in-memory canvas; reconnecting does not reset it or start another listener. Stop the studio with Ctrl+C only after saving your artwork.

**Migrating from the initial stdio build:** disable the old paint Command connection in OpenChamber first, then check `ss -ltnp 'sport = :8765'`. If an old process still owns the port, verify its full command line before terminating it; save any artwork first. Start the updated studio once and change the existing MCP entry to Link. Do not launch the script as a stdio MCP command anymore.

Optional environment variables: PAINT_PORT (default 8765), PAINT_OUTPUT (default artwork/ in repository). The same port serves the viewer and MCP. Use the matching URL if you change it.

Run engine tests with `.venv/bin/python -m unittest -v test_engine`. With the studio running, run `.venv/bin/python test_mcp.py` to verify that two independent MCP connections share the same canvas and that the viewer and image feedback work. **The integration test creates a temporary layer, paints on it and undoes both changes; run it on a fresh studio before painting.**

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

This is an initial implementation, not a validated release. Hard-edged raster marks with basic rounded strokes and cubic curves; no natural-media texture yet. Live viewer refreshes after each operation/batch. Undo retains up to 20 snapshots with a memory budget. Single in-memory document; save before stopping the studio. Disconnecting an MCP client does not stop the studio. Layered archives contain scene metadata and PNG layers, but reopening is not yet implemented. Region snapshots, reference-image import and native desktop packaging are deferred.

See [PROJECT_STATUS.md](PROJECT_STATUS.md) for progress and next actions.

MIT licence.
