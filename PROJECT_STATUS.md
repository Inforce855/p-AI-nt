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

- First E4B painting benchmark passed for basic tool usability on 16 November 2026. Prompt 10:48:11, background by 10:48:43, cat drawn by 10:49:34, session complete 10:49:51 (100 seconds). Five layers, nine successful painting operations; four layer creations and nine marks in one Code Mode execution reported at 86 ms. No painting tool errors. Screenshot confirms orange body/head, pointed pink ears, green eyes and pale blue background. Missing tabby stripes, whiskers, pupils, paws and tail; angular body. look returned image attachment; no corrective edits demonstrated. Saved Orange_Tabby_Cat.png and Orange_Tabby_Cat.paint locally. Evidence: user screenshot and OC Exporter+ Canvas inspection and layers archive _3, successful third user turn.

## REMAINING
- Verify meaningful visual interpretation and correction by E4B or another vision model; image attachment delivery succeeded.
- Compare Gemma 26B and 31B against the successful E4B baseline using the same prompt and tools.
- Improve rendering quality and brush textures after the basic benchmark.
- Add project reopening, persistent recovery, reference images and region inspection for Colliers Farm.
- Desktop packaging deferred.

## NEXT ACTION
Preserve E4B's saved artwork. Run the same cat prompt with Gemma 26B in a fresh conversation, starting a new canvas; compare artistic quality, time, tool errors and visual corrections. No engine changes required for this comparison.

## Verification
Nobara engine tests: 6/6 passed in 0.009 seconds. The original stdio port conflict (Errno 98) occurred when a second process attempted to bind the existing OpenCode-launched viewer's port. The HTTP migration and integration test have now passed according to the user's confirmation; the original conflict is no longer blocking testing. Gemma E4B successfully painted and saved artwork; look returned an image attachment, but meaningful visual correction has not yet been demonstrated. Viewer updates after each committed operation/batch (not individual strokes within a batch). One persistent studio process holds the shared canvas; reconnecting clients preserves state, stopping the studio loses unsaved state. Layered archives retain pixels and layer metadata but reopening is not implemented yet.
