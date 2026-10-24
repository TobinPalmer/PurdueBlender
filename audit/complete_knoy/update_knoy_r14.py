"""Correct Knoy evidence metadata and refine the photo-consistent brick finish.

Only the dedicated Knoy source asset is opened and saved. No mesh geometry,
object transforms, placement data, or roof/story geometry is changed.
"""
import bpy
from pathlib import Path

root = Path(r"C:\Users\Tobin\Documents\Blender\PurdueMap")
blend = root / "modular" / "buildings" / "knoy_hall.blend"
bpy.ops.wm.open_mainfile(filepath=str(blend))

scene = bpy.context.scene
asset_root = bpy.data.objects["AssetRoot_knoy_hall"]
trace_status = (
    "Typical upper-floor source is preserved in audit/complete_knoy/"
    "knoy_typical_plan_crop.png. Hand-registered approximate trace meshes for "
    "the Purdue 2018 Typical Plan Levels 2-4 are present as "
    "KNOY_L2_TypicalPlan_InteriorPartitions, "
    "KNOY_L3_TypicalPlan_InteriorPartitions, and "
    "KNOY_L4_TypicalPlan_InteriorPartitions. The trace is not an as-built survey; "
    "registration remains approximately +/-1 m."
)
basement_status = (
    "Purdue Polytechnic Building Emergency Plan identifies LOWER BASEMENT and "
    "UPPER BASEMENT zones in the building. This confirms two basement-level "
    "zones are in use but provides no architectural floor plan, footprint, datum, "
    "or dimensions; no basement geometry is modeled from this evidence."
)
elevator_status = (
    "Purdue IT printer locator entry knoy1h01-1 says the first-floor printer is "
    "near the back entrance next to LMBS and near elevators. This confirms "
    "first-floor elevator presence and approximate vicinity only; the source "
    "does not locate elevator shafts by dimensions or identify their upper-floor "
    "door positions, so no elevator geometry is modeled from this source."
)
source_urls = (
    "https://old.polytechnic.purdue.edu/schools/engineering-technology/"
    "safety-training/building-emergency-plan; "
    "https://service.purdue.edu/TDClient/32/Purdue/KB/PrintArticle?ID=2428"
)
for owner in (scene, asset_root):
    owner["evidence_plan_trace_status"] = trace_status
    owner["evidence_basement_status"] = basement_status
    owner["evidence_elevator_status"] = elevator_status
    owner["evidence_interior_source_urls_r14"] = source_urls
    owner["evidence_r14_retrieval_date"] = "2026-10-24"

scene["interior_status"] = (
    "Partial plan-derived interior: L1 partition trace from Liu thesis Figure 3.19(d), "
    "and L2-L4 typical partitions from Purdue's 2018 Gateway planning raster. "
    "Both use approximate manual registration; as-built dimensions, room finishes, "
    "most room contents and complete basement-to-roof circulation remain unverified."
)
scene["interior_evidence"] = (
    "L1 trace source: Liu thesis Figure 3.19(d); 18 candidate openings with 12 "
    "illustrative leaves and six unresolved gaps. L2-L4 wall and door proxies derive "
    "from Purdue Gateway 2018 Typical Plan Levels 2-4. Fixtures are symbol-based "
    "interpretations without a legend. Six stair runs are illustrative, based on plan "
    "core footprints, and do not establish a complete or code-compliant route. See "
    "audit/complete_knoy/evidence_round14.json."
)

# Refine the existing procedural finish only. Brick size is retained because
# available imagery is qualitative, not calibrated; color/bump changes target
# the overly pale and strongly outlined look in the R13 close-up.
brick = bpy.data.materials["KNOY_Purdue_Red_Brick"]
nodes = brick.node_tree.nodes
tex = next(n for n in nodes if n.type == "TEX_BRICK")
bsdf = next(n for n in nodes if n.type == "BSDF_PRINCIPLED")
color_mix = next(n for n in nodes if n.type == "MIX" and any(l.from_node == tex for l in brick.node_tree.links))
bump = next(n for n in nodes if n.type == "BUMP" and any(l.from_node == tex for l in brick.node_tree.links))
tex.inputs["Color1"].default_value = (0.145, 0.038, 0.016, 1.0)
tex.inputs["Color2"].default_value = (0.068, 0.016, 0.007, 1.0)
tex.inputs["Mortar"].default_value = (0.24, 0.21, 0.17, 1.0)
tex.inputs["Mortar Size"].default_value = 0.004
tex.inputs["Mortar Smooth"].default_value = 0.0015
color_mix.inputs["Factor"].default_value = 0.10
bsdf.inputs["Roughness"].default_value = 0.78
bump.inputs["Strength"].default_value = 0.18
bump.inputs["Distance"].default_value = 0.004
brick.diffuse_color = (0.145, 0.038, 0.016, 1.0)
brick["r14_material_change"] = (
    "Brick hues and procedural color variation were darkened to better match "
    "Purdue-hosted qualitative red/brown entrance photographs; mortar contrast "
    "and bump were reduced. Brick dimensions and bond pattern remain estimates, "
    "not measured specifications."
)
brick["r14_source_limit"] = (
    "Qualitative, uncalibrated entrance photographs only; exact brick/mortar "
    "color, bond, dimensions, and current all-face material assignment remain unverified."
)

bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(blend))
print("R14_SAVE", blend)
print("TRACE", asset_root["evidence_plan_trace_status"])
print("BASEMENT", asset_root["evidence_basement_status"])
print("ELEVATOR", asset_root["evidence_elevator_status"])
print("BRICK", tuple(tex.inputs["Color1"].default_value), tuple(tex.inputs["Mortar"].default_value), color_mix.inputs["Factor"].default_value, bsdf.inputs["Roughness"].default_value)
