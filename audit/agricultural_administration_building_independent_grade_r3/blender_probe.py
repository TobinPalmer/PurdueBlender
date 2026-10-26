from __future__ import annotations
import hashlib, json
from pathlib import Path
import bpy

ROOT = Path(__file__).resolve().parents[2]
ID = "agricultural_administration_building"
AUDIT = ROOT / "audit" / f"{ID}_independent_grade_r3"
ASSET = ROOT / "modular" / "buildings" / f"{ID}.blend"
EXPORT = AUDIT / "collection_export_probe.blend"
REPORT = AUDIT / "blender_probe.json"
EXPECTED = "Asset_agricultural_administration_building"

bpy.ops.wm.open_mainfile(filepath=str(ASSET))
scene = bpy.context.scene
scene_name = scene.name
collection = bpy.data.collections.get(EXPECTED)
assert scene.name == "Scene"
assert collection is not None
objects = sorted(collection.all_objects, key=lambda o: o.name)
object_names = [o.name for o in objects]
object_count = len(objects)
shell_type = "MESH"
assert objects
shell = bpy.data.objects.get("AGAD_GIS_outline_primary_shell")
assert shell is not None and shell.name in {o.name for o in objects}
assert shell.type == "MESH"
dg = bpy.context.evaluated_depsgraph_get()
ev = shell.evaluated_get(dg)
mesh = ev.to_mesh()
coords = [ev.matrix_world @ v.co for v in mesh.vertices]
assert coords
bounds = [[min(float(p[i]) for p in coords), max(float(p[i]) for p in coords)] for i in range(3)]
zmin = min(float(p.z) for p in coords)
bottom = sorted({(round(float(p.x), 6), round(float(p.y), 6)) for p in coords if abs(float(p.z)-zmin) < 1e-5})
ev.to_mesh_clear()
external_images = []
for obj in objects:
    for slot in obj.material_slots:
        mat = slot.material
        if not mat or not mat.use_nodes:
            continue
        for node in mat.node_tree.nodes:
            if node.type == "TEX_IMAGE" and node.image and node.image.filepath and not node.image.packed_file:
                path = bpy.path.abspath(node.image.filepath, library=node.id_data.library)
                if path and not Path(path).exists():
                    external_images.append(path)
linked_libraries = sorted({str(lib.filepath) for lib in bpy.data.libraries if lib.filepath})
manifest = json.loads((ROOT / "modular" / "manifest.json").read_text(encoding="utf-8"))
entry = next(x for x in manifest["assets"] if x.get("id") == ID)
assert entry["file"].replace("\\", "/") == f"buildings/{ID}.blend"
assert entry["collection"] == EXPECTED
bpy.data.libraries.write(str(EXPORT), {collection}, path_remap="RELATIVE_ALL", fake_user=True)
bpy.ops.wm.open_mainfile(filepath=str(EXPORT))
export_collection = bpy.data.collections.get(EXPECTED)
assert export_collection is not None
export_names = sorted(o.name for o in export_collection.all_objects)
assert len(export_names) == object_count
result = {
    "asset": str(ASSET),
    "asset_sha256": hashlib.sha256(ASSET.read_bytes()).hexdigest(),
    "scene": scene_name,
    "collection": EXPECTED,
    "collection_object_count": object_count,
    "collection_object_names": object_names,
    "shell_name": "AGAD_GIS_outline_primary_shell",
    "shell_type": shell_type,
    "shell_bounds_evaluated_local_m": bounds,
    "shell_min_z_m": zmin,
    "shell_bottom_unique_vertices_xy_m": bottom,
    "expected_manifest_count": entry.get("object_count"),
    "expected_manifest_names": sorted(entry.get("objects", [])),
    "external_unpacked_image_dependencies": sorted(set(external_images)),
    "linked_library_paths": linked_libraries,
    "export_reopened": True,
    "export_collection": EXPECTED,
    "export_object_count": len(export_names),
    "export_object_names_match": export_names == sorted(entry.get("objects", [])),
}
assert result["expected_manifest_count"] == len(objects)
assert sorted(entry.get("objects", [])) == object_names
assert not external_images and not linked_libraries
REPORT.write_text(json.dumps(result, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
print(json.dumps(result, indent=2, ensure_ascii=False))




