"""Save the modular linked master at the project's conventional root filename."""
import bpy
import json
import os
import shutil
from pathlib import Path

MODULAR = Path(__file__).resolve().parent
ROOT = MODULAR.parent
target = ROOT / "purdue_campus_master.blend"
backup = ROOT / "purdue_campus_master_before_modular_linking.blend"
if target.exists() and not backup.exists():
    shutil.copy2(target, backup)

# Keep each source library's absolute location while the master moves directories.
sources = {lib: Path(bpy.path.abspath(lib.filepath)).resolve() for lib in bpy.data.libraries}
bpy.ops.wm.save_as_mainfile(filepath=str(target))
for library, source_path in sources.items():
    relative = os.path.relpath(source_path, ROOT).replace("\\", "/")
    library.filepath = "//" + relative
bpy.ops.wm.save_as_mainfile(filepath=str(target))

resolved = {lib.filepath: str(Path(bpy.path.abspath(lib.filepath)).resolve()) for lib in bpy.data.libraries}
missing = [path for path in resolved.values() if not Path(path).is_file()]
if missing:
    raise RuntimeError("Missing linked source files: " + "; ".join(missing[:10]))
print(json.dumps({"master": str(target), "backup": str(backup) if backup.exists() else None,
                  "libraries": len(resolved), "missing": missing,
                  "resolved_path_sample": list(resolved.values())[:5]}))
