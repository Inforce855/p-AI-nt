# Project status — 16 November 2026

## COMPLETED
- Repository created on main with MIT licence.
- Initial v0.1 implementation: Pillow layered raster engine, nine MCP tools, local read-only live viewer, PNG and layered archive saving, bounded undo, deterministic engine tests.
- Existing GIMP, Krita, Open Paint Studio and OpenChamber configuration remain untouched.
- Design: AI chooses geometry, colour and technique; engine performs operations. No raw Python escape hatch.

## REMAINING
- Run engine tests and MCP integration smoke test on Nobara.
- Verify the actual OpenChamber image feedback path with Gemma E4B.
- Test independent cat painting, then compare Gemma 26B and 31B.
- Improve rendering quality and brush textures after the basic benchmark.
- Add project reopening, persistent recovery, reference images and region inspection for Colliers Farm.
- Desktop packaging deferred.

## NEXT ACTION
Install dependencies in the repository's virtual environment, register paint_server.py as a single stdio MCP server in OpenChamber, open the live viewer, then run the E4B cat benchmark.

## Verification
Initial source committed; no claim of a successful model run or Nobara integration until tested. Viewer updates after each committed operation/batch (not individual strokes within a batch). Single process and canvas; restarting MCP loses unsaved state. Layered archives retain pixels and layer metadata but reopening is not implemented yet.
