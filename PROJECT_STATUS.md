# Project status — 16 November 2026

## COMPLETED
- Repository created on main with MIT licence.
- Live viewer verified in browser: 512 × 512 white canvas, Background layer, revision 1, live status. TCP 127.0.0.1:8765 is owned by Python PID 723980 (user screenshot and ss output, 16 November 2026).
- Nobara installation completed: Python 3.14 environment, Pillow 12.3.0 and MCP 1.30.0. All six engine tests passed in 0.009 seconds (user terminal output, 16 November 2026).
- Initial v0.1 implementation: Pillow layered raster engine, nine MCP tools, local read-only live viewer, PNG and layered archive saving, bounded undo, deterministic engine tests.
- Existing GIMP, Krita, Open Paint Studio and OpenChamber configuration remain untouched.
- Design: AI chooses geometry, colour and technique; engine performs operations. No raw Python escape hatch.

- Second E4B export confirms explicit Code Mode call tools.paint.get_scene({}) returned Unknown tool in 9 ms. Model correctly reported unavailable; no painting attempted.
- Connection lifecycle fix implemented: one loopback Streamable HTTP MCP studio with read-only viewer routes on the same port. Existing painting engine and viewer HTML unchanged. SDK integration test added.
- User confirmed all migration and verification steps passed on Nobara on 16 November 2026: HTTP studio running, OpenChamber paint Link connected, and integration smoke test passed (nine tools, two clients sharing one canvas, PNG feedback, viewer and undo).

## REMAINING
- Verify the actual OpenChamber image feedback path with Gemma E4B.
- Test independent cat painting, then compare Gemma 26B and 31B.
- Improve rendering quality and brush textures after the basic benchmark.
- Add project reopening, persistent recovery, reference images and region inspection for Colliers Farm.
- Desktop packaging deferred.

## NEXT ACTION
Run the independent Gemma E4B cat benchmark using the paint MCP tools, with no supplied geometry or technical assistance. Record time to first mark, elapsed time, tool errors, layers, visual inspection/corrections and final artwork.

## Verification
Nobara engine tests: 6/6 passed in 0.009 seconds. The original stdio port conflict (Errno 98) occurred when a second process attempted to bind the existing OpenCode-launched viewer's port. The HTTP migration and integration test have now passed according to the user's confirmation; the original conflict is no longer blocking testing. Gemma E4B's ability to paint and receive visual feedback in OpenChamber remains untested. Viewer updates after each committed operation/batch (not individual strokes within a batch). One persistent studio process holds the shared canvas; reconnecting clients preserves state, stopping the studio loses unsaved state. Layered archives retain pixels and layer metadata but reopening is not implemented yet.
