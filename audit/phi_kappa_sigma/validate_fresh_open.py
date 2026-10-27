"""Open the saved Blender asset in a new process and verify its library contract."""
import bpy
import json
from pathlib import Path
from mathutils import Vector

root = Path(__file__).resolve().parents[2]
asset = root / "modular" / "buildings" / "massing_phi_kappa_sigma_fid829.blend"
collection_name = "Asset_massing_phi_kappa_sigma_fid829"
scene_name = "Building_massing_phi_kappa_sigma_fid829"
bpy.ops.wm.open_mainfile(filepath=str(asset))
scene = bpy.data.scenes.get(scene_name)
collection = bpy.data.collections.get(collection_name)
assert scene is not None, f"Missing scene {scene_name}"
assert collection is not None, f"Missing collection {collection_name}"
assert collection in list(scene.collection.children), "Expected asset collection linked directly to the library scene"
assert len(bpy.data.scenes) == 1, f"Unexpected scenes: {[s.name for s in bpy.data.scenes]}"
assert len(collection.objects) > 300
assert all(obj.type in {"MESH", "EMPTY"} for obj in collection.objects)
assert not any(img.filepath and not img.packed_file for img in bpy.data.images), "External images are not portable"
mesh_objects = [o for o in collection.objects if o.type == "MESH"]
assert len(mesh_objects) >= 2
roof_caps = [o for o in mesh_objects if "flat roof cap" in o.name]
assert len(roof_caps) == 3, f"Expected 3 single-surface roof caps, got {len(roof_caps)}"
for roof in roof_caps:
    zs = [corner[2] for corner in roof.bound_box]
    assert max(zs) - min(zs) < 0.001, f"Roof cap {roof.name} is a volume, not a surface"
assert scene.get("source_feature_id") == 829
assert len([o for o in mesh_objects if "stepped GIS shell" in o.name]) == 1
height_estimates = json.loads(scene["wing_height_estimates_m"])
assert height_estimates == {"front_house": 10.1, "rear_core": 9.5, "terrace_wing": 6.7}
partition_areas = json.loads(scene["footprint_partition_areas_m2_local"])
assert abs(sum(partition_areas.values()) - scene["footprint_area_m2_local"]) < 0.01
assert len([o for o in mesh_objects if "Terrace_Railing" in o.name]) > 20
brick = bpy.data.materials.get("White painted brick | procedural")
assert brick and brick.node_tree
brick_tex = next(n for n in brick.node_tree.nodes if n.type == "TEX_BRICK")
brick_tex_input = brick_tex.inputs.get("Vector")
assert any(link.to_socket == brick_tex_input and link.from_socket.name == "UV"
           for link in brick.node_tree.links), "Brick shader is not using physical façade UVs"
depsgraph = bpy.context.evaluated_depsgraph_get()
depsgraph.update()
corners = [o.evaluated_get(depsgraph).matrix_world @ Vector(corner)
           for o in mesh_objects for corner in o.evaluated_get(depsgraph).bound_box]
mins = [min(v[axis] for v in corners) for axis in range(3)]
maxs = [max(v[axis] for v in corners) for axis in range(3)]
report = {
    "blend_file": str(asset),
    "scene": scene.name,
    "collection": collection.name,
    "object_count": len(collection.objects),
    "mesh_count": len(mesh_objects),
    "image_count": len(bpy.data.images),
    "external_images": [],
    "roof_caps": [o.name for o in roof_caps],
    "wing_height_estimates_m": height_estimates,
    "footprint_partition_areas_m2_local": partition_areas,
    "footprint_area_m2_local": round(scene["footprint_area_m2_local"], 3),
    "terrace_rail_object_count": len([o for o in mesh_objects if "Terrace_Railing" in o.name]),
    "bounds_world_m": [[round(mins[i], 3), round(maxs[i], 3)] for i in range(3)],
    "passed": True,
}
out = root / "audit" / "phi_kappa_sigma" / "fresh_open_validation.json"
out.write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps(report, indent=2))
