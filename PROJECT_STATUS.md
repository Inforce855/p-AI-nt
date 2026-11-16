# Project status — 16 November 2026

## COMPLETED
- Repository created on main with MIT licence.
- Live viewer verified in browser: 512 × 512 white canvas, Background layer, revision 1, live status. TCP 127.0.0.1:8765 is owned by Python PID 723980 (user screenshot and ss output, 16 November 2026).
- Nobara installation completed: Python 3.14 environment, Pillow 12.3.0 and MCP 1.30.0. All six engine tests passed in 0.009 seconds (user terminal output, 16 November 2026).
- Initial v0.1 implementation: Pillow layered raster engine, nine MCP tools, local read-only live viewer, PNG and layered archive saving, bounded undo, deterministic engine tests.
- Existing GIMP, Krita, Open Paint Studio and OpenChamber configuration remain untouched.
- Design: AI chooses geometry, colour and technique; engine performs operations. No raw Python escape hatch.

## REMAINING
- Resolve the viewer port 8765 bind conflict reported by OpenChamber; identify the command line and parent of Python PID 723980 before changing code or stopping anything.
- Run MCP integration smoke test on Nobara.
- Verify the actual OpenChamber image feedback path with Gemma E4B.
- Test independent cat painting, then compare Gemma 26B and 31B.
- Improve rendering quality and brush textures after the basic benchmark.
- Add project reopening, persistent recovery, reference images and region inspection for Colliers Farm.
- Desktop packaging deferred.

## NEXT ACTION
Inspect PID 723980 and its parent with ps to establish which launch owns the working viewer. Resolve the duplicate bind or stale process, then verify MCP tool discovery and shared-canvas updates before the E4B benchmark.

## Verification
Initial source committed and engine tests passed on Nobara. OpenChamber startup currently fails with Errno 98 (address already in use) on port 8765; viewer confirmed working in an existing Python process (PID 723980). Process launch and ownership not yet established. No successful MCP integration or model run claimed. Viewer updates after each committed operation/batch (not individual strokes within a batch). Single process and canvas; restarting MCP loses unsaved state. Layered archives retain pixels and layer metadata but reopening is not implemented yet.
