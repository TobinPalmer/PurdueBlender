# Dudley Hall evidence and build notes

The current library keeps the original Purdue GIS footprint and campus-coordinate frame, then adds a schematic facade treatment grounded in the architect's published exterior photograph and Purdue's building description. The building is still a campus-coordinate massing asset in the shared manifest; any change to manifest kind, index, or integration handoff belongs to the coordinator after independent review.

The saved GIS source is feature 432 / code DUDL. Its largest ring describes the horizontal plan only. The structural shell matches the ring to 0.0001 m by symmetric nearest XY vertex comparison. This confirms the source outline correspondence; it does not validate building identity beyond the official GIS attributes or prove facades, height, roof elevation, or basement depth.

The architect's 2023 exterior photo shows red brick wall areas, a broad multi-story glass entrance, a pale projecting facade volume, and a terracotta-colored screen on the connected gateway complex. The model uses these as broad visual cues. The photograph shows both Dudley and Lambertus; its visible components cannot be assigned to Dudley's footprint with survey-level certainty. Purdue's 2019 announcement gives Dudley as four stories with a basement and approximately 145,000 square feet. Ennead's 250,000 GSF figure and Purdue's later 255,000 square-foot figure describe the combined complex, so neither is used as Dudley's individual area.

The shell's 16.0 m height and all facade levels are estimates. No certified heights or facade elevations were found. The GIS attributes likewise state that height is unverified.

Run the builder from the repository root:

```powershell
& "C:\path\to\blender.exe" --background --python modular/buildings/build_dudley_hall.py
```

Then reopen and validate the saved asset:

```powershell
& "C:\path\to\blender.exe" --background --python audit/dudley_hall/verify_asset.py
```

The last generated view is `views/dudley_hall_refined_preview.png`. Structured sources and asset checks are saved in this folder. An independent grade has not yet been assigned; do not treat this asset as a passing handoff until a separate grader returns at least 8/10.
