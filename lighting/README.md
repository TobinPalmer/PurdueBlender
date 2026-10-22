# Campus Time Sky

The lighting is a self-contained procedural world with peach and lavender dusk, pink cloud layers, a warm directional sun, and a restrained blue fill. It needs no downloaded textures or third-party libraries. Default time is **18:00 (sunset)** when first built. This is an artistic 24-hour cycle, not a date/location solar calculator. Clouds are a distant world shader, not nearby volumetric geometry.

## Change the time

Open the lighting-enabled scene. In Scene Properties > Custom Properties, edit `campus_time` between 0 and 24. Use Rendered viewport shading (with Scene World and Scene Lights enabled) or render to see the result. Dawn is 6, noon 12, sunset 18, night 0. The core saved lighting works without enabling automatic Python execution.

For a convenient sidebar, open `campus_time.py` in Blender's Text Editor and Run Script once. In the 3D View press N and open **Campus Sky**. Change the Time slider or use Dawn / Noon / Sunset / Night. Running the script again preserves the current time, rebuilds the sky, and avoids accumulating driver variables. The optional panel must be registered again after a Blender restart; the saved sky itself remains functional. Advanced users may install the script as a legacy add-on to retain the panel; apply the sky once by running the script first.

## Preservation and integration

The previous local world remains in the file with a fake user; linked worlds are left untouched; its name is recorded in Scene `campus_previous_world`. Linked non-Campus suns are excluded through local shallow collection copies that retain all other linked contents; their source libraries remain untouched. Original local non-Campus sun lights have their prior energy stored as `campus_original_energy` on their light data and are set to zero to avoid double illumination. Other light types remain unchanged. Return to the prior world and restore those energies to undo the lighting; keep the original project backup for a complete rollback.

The final lighting uses exposure -0.65 and a 512 MB EEVEE shadow pool to accommodate the campus lights. It does not replace building materials or geometry. Use `build_sky(scene)` from Python to apply; when changing `scene['campus_time']` from Python, call `scene.update_tag()` followed by a frame/dependency update. `register()` and `unregister()` manage the optional panel.

The finished lighting is applied to `../purdue_campus_master.blend`, with the previous saved master preserved at `master_before_final_sunset.blend`. A separate sunset copy is retained at `../purdue_campus_sunset.blend`. Three rendered images are in `renders/`. The optional Campus Sky panel was installed as a local Blender add-on, so it is available after restarting Blender.

## Verified implementation

Tested in Blender **5.2.2 LTS** in a separate minimal scene, with `--disable-autoexec`:

- Repeated sky construction succeeded, and panel registration/unregistration succeeded.
- Every sky and sun driver was valid and a native simple expression at all four test times. Color-ramp driver paths resolved successfully.
- At 0 / 6 / 12 / 18 hours, sun energy evaluated to **0 / 0.712067 / 3.2 / 0.712067** and world strength to **0.14 / 0.283 / 0.69 / 0.36**.
- Saved the verification scene, reopened it with automatic Python execution disabled, and repeated all four time tests successfully. The optional Python UI was not required for evaluation.

The sky direction uses negative World Texture Coordinate Normal so altitude/cloud fading follows the outward viewing hemisphere. Campus building framing and final visual quality are checked separately in the render workflow.
