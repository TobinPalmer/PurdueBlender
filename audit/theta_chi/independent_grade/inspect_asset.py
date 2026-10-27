"""Fresh-process Blender inspection for the independent Theta Chi grade."""
import bpy
import json
import sys
from pathlib import Path

args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
if len(args) != 2:
    raise SystemExit("usage: blender asset.blend --python inspect_asset.py -- asset.blend output.json")
asset_path, output_path = map(Path, args)
bpy.ops.wm.open_mainfile(filepath=str(asset_path))
expected = "Asset_massing_house_301841328_39f169f"
collection = bpy.data.collections.get(expected)
objects = list(collection.objects) if collection else []
mesh_objects = [o for o in objects if o.type == "MESH"]
result = {
    "asset_path": str(asset_path),
    "blender_version": bpy.app.version_string,
    "expected_collection_found": collection is not None,
    "collection_object_count": len(objects),
    "objects": [],
    "external_images": [im.filepath for im in bpy.data.images if im.source == "FILE"],
    "linked_libraries": [lib.filepath for lib in bpy.data.libraries],
}
for obj in objects:
    row = {"name": obj.name, "type": obj.type, "location": list(obj.location), "rotation": list(obj.rotation_euler), "scale": list(obj.scale), "modifiers": [m.name for m in obj.modifiers]}
    if obj.type == "MESH":
        deps = bpy.context.evaluated_depsgraph_get()
        ev = obj.evaluated_get(deps)
        mesh = ev.to_mesh()
        verts = [tuple(v.co) for v in mesh.vertices]
        row.update({"vertex_count": len(mesh.vertices), "edge_count": len(mesh.edges), "face_count": len(mesh.polygons), "materials": [m.name if m else None for m in mesh.materials],
                    "bounds_local": [[min(v[i] for v in verts), max(v[i] for v in verts)] for i in range(3)],
                    "z0_vertices": sum(abs(v[2]) < 1e-6 for v in verts),
                    "z0_xy_vertices": sorted([[v[0], v[1]] for v in verts if abs(v[2]) < 1e-6]),
                    "z_levels_rounded_01m": sorted({round(v[2], 1) for v in verts})})
        ev.to_mesh_clear()
    result["objects"].append(row)
output_path.parent.mkdir(parents=True, exist_ok=True)
output_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps(result, indent=2))
