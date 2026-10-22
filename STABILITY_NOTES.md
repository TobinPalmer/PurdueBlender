# PurdueMap stability work — October 22, 2026

The master file has been opened in Blender 5.2.2 LTS and saved with repaired viewport settings. The untouched original is `purdue_campus_master.pre_stability_fix.blend`. The original crash report is preserved in `original_crash.txt`.

## Evidence

The existing crash report records an access violation inside EEVEE's `ShadowTileMap::sync_orthographic`, reached through directional sun-shadow synchronization during viewport drawing. This is a native Blender crash, not a Python exception. The exact triggering interaction was not reproduced in this session.

The saved Layout viewport had an orbit distance of zero. That degenerate navigation state was repaired. Viewport clipping was adjusted from 0.01–1000 to 0.1–10000 to suit the campus scale. The project now opens in Solid shading with a useful aerial camera view, avoiding immediate shader/shadow work on startup. Material Preview and Rendered shading remain available. No geometry, materials, cameras, light settings, or render engine were removed or simplified.

## Checks

- Background file load and clean process exit succeeded.
- All 15,745 objects retained, including 110 cameras and 305 lights.
- No nonfinite object transforms or mesh vertex coordinates found.
- No missing external image files found.
- No invalid camera clipping intervals or zero orthographic camera scales found.
- Live rendered perspective and top orthographic campus views succeeded with sun shadows enabled.
- Three EEVEE PNG renders at 25% resolution succeeded: PMU aerial, Haas exterior, Haas rotunda interior. See `stability_verification.json` and `stability_render.log`.
- Saved master reopened successfully in the live Blender session.

## Limits

These changes repair a suspicious saved viewport state and provide a safer startup configuration. They do not patch Blender's native EEVEE implementation. Since the original access violation was not reproduced, its underlying cause remains unconfirmed. All 110 camera renders and extended interactive use have not been exhaustively tested. A recurring crash needs the specific interaction and a fresh crash report to isolate further.
