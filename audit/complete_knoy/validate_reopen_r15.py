"""Reopen Knoy after R15 material-only tuning; ensure all geometry is preserved."""
import bpy, hashlib, json
from pathlib import Path

ROOT = Path(r"C:\Users\Tobin\Documents\Blender\PurdueMap")
BLEND = ROOT / "modular" / "buildings" / "knoy_hall.blend"
OUT = ROOT / "audit" / "complete_knoy" / "validation_round15.json"
bpy.ops.wm.open_mainfile(filepath=str(BLEND))
asset = bpy.data.collections["Asset_knoy_hall"]
scene = bpy.context.scene
root = bpy.data.objects["AssetRoot_knoy_hall"]
assert len(asset.objects) == 64 and len(asset.all_objects) == 157
expected = {
    "KNOY_UpperLevel_TypicalPartitions_L2-L4": 3,
    "KNOY_TypicalPlan_StairRuns_L2-L4": 6,
    "KNOY_TypicalPlan_Doors_L2-L4": 45,
    "KNOY_TypicalPlan_WashroomFixtures_L2-L4": 39,
}
children = {c.name: c for c in asset.children}
assert {name: len(children[name].objects) for name in expected} == expected
assert "L2-L4 typical partitions" in scene["interior_status"]
assert "are not yet traced" not in root["evidence_plan_trace_status"]

h = hashlib.sha256()
mesh_count = 0
for obj in sorted(asset.all_objects, key=lambda o: o.name):
    if obj.type != "MESH":
        continue
    mesh_count += 1
    h.update(obj.name.encode())
    for row in obj.matrix_world:
        h.update(",".join(f"{v:.8f}" for v in row).encode())
    for vertex in obj.data.vertices:
        h.update(",".join(f"{v:.8f}" for v in vertex.co).encode())
    for poly in obj.data.polygons:
        h.update(",".join(str(i) for i in poly.vertices).encode())
mesh_hash = h.hexdigest()
assert mesh_count == 156
assert mesh_hash == "43a19a6313c06e188082cb547847f583573bafe7f6d9e9ec6da52706b36de5b4", mesh_hash

mat = bpy.data.materials["KNOY_Purdue_Red_Brick"]
nodes = mat.node_tree.nodes
brick = next(n for n in nodes if n.type == "TEX_BRICK")
mix = next(n for n in nodes if n.type == "MIX" and any(l.from_node == brick for l in mat.node_tree.links))
assert round(brick.inputs["Mortar Size"].default_value, 3) == 0.003
assert round(mix.inputs["Factor"].default_value, 2) == 0.04
assert tuple(round(v, 2) for v in brick.inputs["Mortar"].default_value[:3]) == (0.14, 0.12, 0.10)
assert not [i.filepath for i in bpy.data.images if i.source == "FILE" and i.filepath]
report = {
    "reopened_saved_asset": "PASS",
    "asset": str(BLEND),
    "revision": 15,
    "direct_objects": len(asset.objects),
    "descendant_objects": len(asset.all_objects),
    "nested_counts": expected,
    "trace_status_current": True,
    "all_156_mesh_geometry_and_world_matrices_match_r14": True,
    "mesh_sha256": mesh_hash,
    "brick_mortar_linear": list(brick.inputs["Mortar"].default_value),
    "estimated_mortar_width_m": brick.inputs["Mortar Size"].default_value,
    "brick_noise_mix_factor": mix.inputs["Factor"].default_value,
    "external_image_dependencies": [],
    "roof_L5_penthouse_PV_placement_unchanged": True,
    "result": "PASS",
}
OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, indent=2))
