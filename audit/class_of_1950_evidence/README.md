# Class of 1950 building evidence

This folder holds the source snapshots and repeatable validation record for the current modular Class of 1950 asset. The authoring `.blend` remains the geometry source of truth. The legacy top-level `build_class_of_1950.py` and `refine_class_of_1950.py` operate on full scenes and are not safe to rerun against the modular master; they do not reproduce every later correction by themselves.

Run the canonical packaging validator with (the asset was authored by a Blender 5.02-series build; 4.5.15 opens and validates it but logs a future-version warning and an unavailable `BLENDER_EEVEE` engine message, while the loaded scene reports `BLENDER_EEVEE_NEXT`):

```powershell
& "C:\Users\gotse\Documents\Codex\2026-10-25\github-plugin-github-openai-curated-remote\outputs\blender\blender-4.5.15-windows-x64\blender.exe" -b --python modular/buildings/build_class_of_1950.py
```

To test a portable byte-identical package without overwriting the source:

```powershell
& "C:\Users\gotse\Documents\Codex\2026-10-25\github-plugin-github-openai-curated-remote\outputs\blender\blender-4.5.15-windows-x64\blender.exe" -b --python modular/buildings/build_class_of_1950.py -- --package-copy work/class_of_1950_package_test.blend
```

`package_validation.json` records reopen validation, collection/object/material checks, local-frame bounds, dependencies, and the current source-data limitations. No campus master, manifest, README, or shared index is edited.
