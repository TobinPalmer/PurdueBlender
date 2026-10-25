import bpy
import hashlib
import json
from pathlib import Path
from mathutils import Vector

ROOT = Path(r"C:/Users/Tobin/Documents/Blender/PurdueMap")
ASSET = ROOT / "modular/buildings/potter_engineering.blend"
OUT = ROOT / "audit/potter_engineering_refine/independent_grade_probe.json"
bpy.ops.wm.open_mainfile(filepath=str(ASSET))

coll = bpy.data.collections.get("Asset_potter_engineering")
root = bpy.data.objects.get("AssetRoot_potter_engineering")
shell = bpy.data.objects.get("POTR_Official_864_Structural_Envelope")
roof = bpy.data.objects.get("POTR_Official_864_Roof")
assert coll and root and shell and roof

def world_bounds(obj):
    pts = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    return [[round(min(p[i] for p in pts), 5), round(max(p[i] for p in pts), 5)] for i in range(3)]

def world_ray_hit(obj, origin, direction):
    inv = obj.matrix_world.inverted()
    o = inv @ Vector(origin)
    d = (inv.to_3x3() @ Vector(direction)).normalized()
    return bool(obj.ray_cast(o, d)[0])

meshes = [o for o in coll.all_objects if o.type == "MESH"]
no_material = [o.name for o in meshes if not o.data.materials]
missing_images = [i.filepath for i in bpy.data.images if i.source == "FILE" and not i.packed_file and not Path(bpy.path.abspath(i.filepath)).exists()]
result = {
    "saved_asset_opened_read_only": True,
    "asset_sha256": hashlib.sha256(ASSET.read_bytes()).hexdigest().upper(),
    "scene": bpy.context.scene.name,
    "collection_exists": coll.name,
    "collection_objects": len(coll.all_objects),
    "collection_meshes": len(meshes),
    "root_location": [round(float(v), 6) for v in root.location],
    "shell_world_bounds_m": world_bounds(shell),
    "roof_world_bounds_m": world_bounds(roof),
    "materialless_meshes": no_material,
    "missing_external_images": missing_images,
    "roof_opening_test": {
        "opening_center_clear": not world_ray_hit(roof, (10.5, 35.2, 20.0), (0, 0, -1)),
        "west_control_intersects_roof": world_ray_hit(roof, (8.5, 35.2, 20.0), (0, 0, -1)),
        "east_control_intersects_roof": world_ray_hit(roof, (12.3, 35.2, 20.0), (0, 0, -1)),
        "estimated_opening_bounds_xy_m": [8.7, 33.85, 12.1, 36.55],
    },
}
OUT.write_text(json.dumps(result, indent=2))
print(json.dumps(result, indent=2))
