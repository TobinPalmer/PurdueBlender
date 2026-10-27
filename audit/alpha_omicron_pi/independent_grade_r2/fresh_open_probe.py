"""Independent fresh-open probe for the revised AOII candidate."""
import hashlib
import json
from collections import Counter
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(bpy.data.filepath).resolve().parents[2]
ASSET_ID = "massing_house_970455277_a3fb72a"
EXPECTED_SHA = "3ac83c2841058b6de3a7f19c587e151df6b3751589a82f03ec4f1c6460da5ec7"
path = Path(bpy.data.filepath).resolve()
sha = hashlib.sha256(path.read_bytes()).hexdigest()
scene = bpy.data.scenes.get(f"Building_{ASSET_ID}")
collection = bpy.data.collections.get(f"Asset_{ASSET_ID}")
errors = []
if sha != EXPECTED_SHA:
    errors.append(f"SHA mismatch: {sha}")
if scene is None or collection is None:
    errors.append("Expected scene or asset collection missing")

objects = list(collection.all_objects) if collection else []
meshes = [o for o in objects if o.type == "MESH"]
material_names = sorted({m.name for o in meshes for m in o.data.materials if m})
linked = [str(lib.filepath) for lib in bpy.data.libraries if lib.filepath]
file_images = [img.filepath for img in bpy.data.images
               if img.source == "FILE" and img.filepath and not img.packed_file]
points = [o.matrix_world @ Vector(corner) for o in meshes for corner in o.bound_box]
bounds = [[min(p[i] for p in points), max(p[i] for p in points)] for i in range(3)] if points else None

slab = bpy.data.objects.get("AOII_Level_1_Slab")
slab_ring = []
slab_ring_z = None
if slab is None or slab.type != "MESH":
    errors.append("AOII_Level_1_Slab missing")
else:
    z_values = [float((slab.matrix_world @ v.co).z) for v in slab.data.vertices]
    slab_ring_z = min(z_values)
    seen = set()
    for v in slab.data.vertices:
        p = slab.matrix_world @ v.co
        if abs(float(p.z) - slab_ring_z) < 1e-5:
            xy = (round(float(p.x), 8), round(float(p.y), 8))
            if xy not in seen:
                slab_ring.append(xy)
                seen.add(xy)

result = {
    "asset": str(path),
    "sha256": sha,
    "expected_sha256": EXPECTED_SHA,
    "blender_version": bpy.app.version_string,
    "scene_name": scene.name if scene else None,
    "collection_name": collection.name if collection else None,
    "object_count": len(objects),
    "mesh_count": len(meshes),
    "object_type_counts": dict(Counter(o.type for o in objects)),
    "used_material_count": len(material_names),
    "used_material_names": material_names,
    "linked_libraries": linked,
    "unpacked_file_images": file_images,
    "bounds_local_m": bounds,
    "slab_name": slab.name if slab else None,
    "slab_lowest_ring_z_m": slab_ring_z,
    "slab_ring_xy_local_m": slab_ring,
    "errors": errors,
}
out = ROOT / "audit" / "alpha_omicron_pi" / "independent_grade_r2" / "fresh_open_probe.json"
out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2, ensure_ascii=False))
if errors:
    raise RuntimeError("AOII R2 fresh-open probe failed")
