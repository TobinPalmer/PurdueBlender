"""Reopen and verify the Knoy R14 source asset and evidence corrections."""
import bpy, hashlib, json
from pathlib import Path

ROOT = Path(r"C:\Users\Tobin\Documents\Blender\PurdueMap")
BLEND = ROOT / "modular" / "buildings" / "knoy_hall.blend"
PRE_R14 = ROOT / "audit" / "complete_knoy" / "knoy_hall_before_r14.blend"
OUT = ROOT / "audit" / "complete_knoy" / "validation_round14.json"

def geometry_fingerprint():
    asset_local = bpy.data.collections["Asset_knoy_hall"]
    h = hashlib.sha256()
    count = 0
    for obj in sorted(asset_local.all_objects, key=lambda o: o.name):
        if obj.type != "MESH":
            continue
        count += 1
        h.update(obj.name.encode())
        for row in obj.matrix_world:
            h.update(",".join(f"{v:.8f}" for v in row).encode())
        for v in obj.data.vertices:
            h.update(",".join(f"{c:.8f}" for c in v.co).encode())
        for poly in obj.data.polygons:
            h.update(",".join(str(i) for i in poly.vertices).encode())
    return count, h.hexdigest()

bpy.ops.wm.open_mainfile(filepath=str(PRE_R14))
pre_count, pre_hash = geometry_fingerprint()
bpy.ops.wm.open_mainfile(filepath=str(BLEND))
current_count, current_hash = geometry_fingerprint()
assert current_count == pre_count and current_hash == pre_hash, (pre_count, pre_hash, current_count, current_hash)
asset = bpy.data.collections["Asset_knoy_hall"]
root = bpy.data.objects["AssetRoot_knoy_hall"]
scene = bpy.context.scene
assert len(asset.objects) == 64 and len(asset.all_objects) == 157
children = {c.name: c for c in asset.children}
expected = {
    "KNOY_UpperLevel_TypicalPartitions_L2-L4": 3,
    "KNOY_TypicalPlan_StairRuns_L2-L4": 6,
    "KNOY_TypicalPlan_Doors_L2-L4": 45,
    "KNOY_TypicalPlan_WashroomFixtures_L2-L4": 39,
}
assert {name: len(children[name].objects) for name in expected} == expected
for owner in (scene, root):
    text = owner["evidence_plan_trace_status"]
    assert "partitions" in text.lower() and "are not yet traced" not in text.lower()
    assert "LOWER BASEMENT" in owner["evidence_basement_status"]
    assert "UPPER BASEMENT" in owner["evidence_basement_status"]
    assert "near the back entrance" in owner["evidence_elevator_status"]
assert "L2-L4 typical partitions" in scene["interior_status"]
assert "complete or code-compliant route" in scene["interior_evidence"]

hash_obj = hashlib.sha256()
shell_count = 0
for obj in sorted(asset.objects, key=lambda o: o.name):
    if obj.type != "MESH" or obj.name == "KNOY_Entrance_Sign_Lettering":
        continue
    shell_count += 1
    hash_obj.update(obj.name.encode())
    for row in obj.matrix_world:
        hash_obj.update(",".join(f"{v:.8f}" for v in row).encode())
    for v in obj.data.vertices:
        hash_obj.update(",".join(f"{c:.8f}" for c in v.co).encode())
    for poly in obj.data.polygons:
        hash_obj.update(",".join(str(i) for i in poly.vertices).encode())
shell_hash = hash_obj.hexdigest()
assert shell_count == 62
assert shell_hash == "c51a34c4704891f3442b17f7df0d9edc3741fc1cee7416041858dbeed39c9ed1", shell_hash

brick = bpy.data.materials["KNOY_Purdue_Red_Brick"]
nodes = brick.node_tree.nodes
tex = next(n for n in nodes if n.type == "TEX_BRICK")
bsdf = next(n for n in nodes if n.type == "BSDF_PRINCIPLED")
mix = next(n for n in nodes if n.type == "MIX" and any(l.from_node == tex for l in brick.node_tree.links))
assert tuple(round(x, 3) for x in tex.inputs["Color1"].default_value[:3]) == (0.145, 0.038, 0.016)
assert round(tex.inputs["Mortar Size"].default_value, 4) == 0.004
assert round(bsdf.inputs["Roughness"].default_value, 2) == 0.78
assert round(mix.inputs["Factor"].default_value, 2) == 0.10
assert not [img.filepath for img in bpy.data.images if img.source == "FILE" and img.filepath]
report = {
    "reopened_saved_asset": "PASS",
    "asset": str(BLEND),
    "revision": 14,
    "direct_objects": len(asset.objects),
    "descendant_objects": len(asset.all_objects),
    "nested_counts": expected,
    "trace_metadata_corrected": True,
    "interior_status_updated": True,
    "two_basement_zones_documented_without_geometry_claim": True,
    "first_floor_elevator_vicinity_documented_without_geometry_claim": True,
    "brick_finish_values": {
        "color_1_linear": list(tex.inputs["Color1"].default_value),
        "color_2_linear": list(tex.inputs["Color2"].default_value),
        "mortar_linear": list(tex.inputs["Mortar"].default_value),
        "estimated_mortar_size_m": tex.inputs["Mortar Size"].default_value,
        "roughness": bsdf.inputs["Roughness"].default_value,
        "color_variation_mix": mix.inputs["Factor"].default_value,
    },
    "unchanged_shell_mesh_count": shell_count,
    "unchanged_shell_mesh_sha256": shell_hash,
    "all_mesh_geometry_and_world_matrices_equal_to_pre_r14": current_count == pre_count and current_hash == pre_hash,
    "pre_r14_mesh_count": pre_count,
    "pre_r14_mesh_sha256": pre_hash,
    "external_image_dependencies": [],
    "roof_L5_penthouse_PV_placement_and_all_mesh_geometry_changed": False,
    "result": "PASS",
}
OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, indent=2))
