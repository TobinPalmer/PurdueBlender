"""Verify a clean probe file can reopen the Triangle library as a link."""

import json
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "audit" / "triangle"
ASSET_ID = "massing_triangle_fraternity_8477ad9"
COLLECTION = f"Asset_{ASSET_ID}"
OBJECT = "Triangle Fraternity"
PROBE = EVIDENCE / "portable_probe.blend"


def main():
    assert Path(bpy.data.filepath).resolve() == PROBE.resolve()
    col = next((c for c in bpy.data.collections if c.name.startswith(COLLECTION)), None)
    assert col is not None
    assert col.library is not None and col.library.filepath
    assert len(col.objects) == 1 and col.objects[0].name == OBJECT
    obj = col.objects[0]
    pts = [obj.matrix_world @ Vector(v) for v in obj.bound_box]
    bounds = [[min(p[i] for p in pts), max(p[i] for p in pts)] for i in range(3)]
    result = {
        "passed": True,
        "blender_version": bpy.app.version_string,
        "probe_path": str(PROBE.relative_to(ROOT)).replace("\\", "/"),
        "linked_collection": col.name,
        "linked_library_path": col.library.filepath,
        "object_count": len(col.objects),
        "object_name": obj.name,
        "object_is_linked": obj.library is not None,
        "mesh_is_linked": obj.data.library is not None,
        "world_bounds_m": bounds,
    }
    (EVIDENCE / "portable_probe_reopen.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
