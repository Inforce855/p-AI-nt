# Project status — 16 November 2026

## COMPLETED
- Repository created on main with MIT licence.
- Live viewer verified in browser: 512 × 512 white canvas, Background layer, revision 1, live status. TCP 127.0.0.1:8765 is owned by Python PID 723980 (user screenshot and ss output, 16 November 2026).
- Nobara installation completed: Python 3.14 environment, Pillow 12.3.0 and MCP 1.30.0. All six engine tests passed in 0.009 seconds (user terminal output, 16 November 2026).
- Initial v0.1 implementation: Pillow layered raster engine, nine MCP tools, local read-only live viewer, PNG and layered archive saving, bounded undo, deterministic engine tests.
- Existing GIMP, Krita, Open Paint Studio and OpenChamber configuration remain untouched.
- Design: AI chooses geometry, colour and technique; engine performs operations. No raw Python escape hatch.

- Second E4B export confirms explicit Code Mode call tools.paint.get_scene({}) returned Unknown tool in 9 ms. Model correctly reported unavailable; no painting attempted.
- Connection lifecycle fix implemented: one loopback Streamable HTTP MCP studio with read-only viewer routes on the same port. Existing painting engine and viewer HTML unchanged. SDK integration test added; runtime verification pending.

## REMAINING
- Migrate existing paint MCP entry from Command (stdio) to Link (HTTP), stop the confirmed old process if still present, and start the studio once. Verify two clients share the canvas and the OpenChamber tool catalogue exposes paint.
- Run MCP integration smoke test on Nobara.
- Verify the actual OpenChamber image feedback path with Gemma E4B.
- Test independent cat painting, then compare Gemma 26B and 31B.
- Improve rendering quality and brush textures after the basic benchmark.
- Add project reopening, persistent recovery, reference images and region inspection for Colliers Farm.
- Desktop packaging deferred.

## NEXT ACTION
Disable old Command MCP, check port ownership, pull the fix, start studio once, configure paint Link to http://127.0.0.1:8765/mcp, and run the integration smoke test. Then E4B cat benchmark.

## Verification
Initial source committed and engine tests passed on Nobara. OpenChamber startup currently fails with Errno 98 (address already in use) on port 8765; viewer confirmed working in an existing Python process (PID 723980). ps confirms PID 723980 is the p-AI-nt virtual-environment Python process, parent PID 289020 is OpenChamber's bundled OpenCode server. A further launch failed to bind the same port; whether it was a connection test or another launch is not established. No successful MCP integration or model run claimed. Viewer updates after each committed operation/batch (not individual strokes within a batch). Single persistent studio process and canvas; reconnecting clients should preserve state, stopping the studio loses unsaved state. HTTP migration not yet tested on Nobara. Layered archives retain pixels and layer metadata but reopening is not implemented yet.
