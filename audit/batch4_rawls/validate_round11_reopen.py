"""Fresh-reopen R11 validation; compares plan shell/panes against exact R10 baseline."""
import bpy, hashlib, json, re
from pathlib import Path
from mathutils import Vector

root=Path(__file__).resolve().parents[2]
baseline=Path(__file__).with_name("rawls_hall_r10_candidate.blend")
asset=root/"modular/buildings/rawls_hall.blend"
out=Path(__file__).with_name("round11_reopen_validation.json")

def geometry_signature(obj):
    return {
        "type":obj.type,
        "location":[round(float(x),6) for x in obj.location],
        "rotation":[round(float(x),6) for x in obj.rotation_euler],
        "scale":[round(float(x),6) for x in obj.scale],
        "vertices":[tuple(round(float(c),6) for c in v.co) for v in obj.data.vertices] if obj.type=="MESH" else None,
        "faces":[tuple(p.vertices) for p in obj.data.polygons] if obj.type=="MESH" else None,
    }

def structural_snapshot(path):
    bpy.ops.wm.open_mainfile(filepath=str(path))
    names=[o.name for o in bpy.data.objects if o.name.startswith("RAWL_2026_Plan1086_") or o.name in {"RAWL_SE_Diagonal_CurtainWall_Glass","RAWL_Masonry_Exterior_Walls"}]
    return {name:geometry_signature(bpy.data.objects[name]) for name in sorted(names)}

baseline_geometry=structural_snapshot(baseline)
bpy.ops.wm.open_mainfile(filepath=str(asset))
scene=bpy.context.scene
scene_objects=list(scene.objects)
get=lambda pattern:[o for o in scene_objects if re.fullmatch(pattern,o.name)]
desks=get(r"RAWL_2026_1086_Desk(?:\.\d{3})?")
chairs=[o for o in scene_objects if o.type=="MESH" and (re.fullmatch(r"RAWL_2026_1086_Chair(?:\.\d{3})?",o.name) or o.name.startswith("RAWL_2026_1086_Chair_R11_Seat_"))]
screens=[bpy.data.objects.get(f"RAWL_1086_R10_Schematic_Projection_Surface_{i:02d}") for i in (1,2)]
contents=[o for o in scene_objects if o.name.startswith("RAWL_1086_R11_Projector_Content_")]
tiers=[o for o in scene_objects if o.name.startswith("RAWL_1086_R10_Schematic_Tier_")]
root_obj=bpy.data.objects["AssetRoot_rawls_hall"]
glass=bpy.data.objects["RAWL_SE_Diagonal_CurtainWall_Glass"]
after_geometry={name:geometry_signature(bpy.data.objects[name]) for name in baseline_geometry}
geometry_changes=[name for name in baseline_geometry if baseline_geometry[name]!=after_geometry.get(name)]
materialless=[o.name for o in scene_objects if o.type=="MESH" and not o.data.materials]
missing_images=[{"name":i.name,"filepath":i.filepath,"packed":bool(i.packed_file)} for i in bpy.data.images if i.source=="FILE" and (not i.packed_file and not Path(bpy.path.abspath(i.filepath)).exists())]
glass_mat=bpy.data.materials["RAWL_CurtainWall_Glass"]
bsdf=next(n for n in glass_mat.node_tree.nodes if n.type=="BSDF_PRINCIPLED")
report={
    "validation":"Blender 5.2.3 fresh reopen",
    "asset":str(asset.resolve()),
    "sha256":hashlib.sha256(asset.read_bytes()).hexdigest(),
    "r10_baseline_sha256":hashlib.sha256(baseline.read_bytes()).hexdigest(),
    "scene_object_count":len(scene_objects),
    "scene_mesh_count":sum(o.type=="MESH" for o in scene_objects),
    "root_world_matrix":[[round(float(v),7) for v in row] for row in root_obj.matrix_world],
    "source_guide":"Purdue RAWL 1086 Classroom Guide (2023), accessed 2026-10-25; source lists 62 seats, fixed tiered tables, lecturer and dual projectors.",
    "desk_objects":len(desks),
    "chair_objects":len(chairs),
    "modeled_chair_object_count":len(chairs),
    "r11_additional_schematic_chairs":sum(o.name.startswith("RAWL_2026_1086_Chair_R11_Seat_") for o in chairs),
    "projection_surfaces":len([o for o in screens if o is not None]),
    "projection_content_cues":len(contents),
    "lectern_parts":sum(o.name.startswith("RAWL_1086_R10_Schematic_Lectern_") for o in scene_objects),
    "schematic_tier_platforms":len(tiers),
    "se_glass_pane_count":len(glass.data.polygons),
    "baseline_structural_objects_compared":len(baseline_geometry),
    "structural_geometry_changes_from_r10":geometry_changes,
    "glass_material":{"base_color":list(bsdf.inputs["Base Color"].default_value),"roughness":float(bsdf.inputs["Roughness"].default_value),"transmission":float(bsdf.inputs["Transmission Weight"].default_value),"specular_ior":float(bsdf.inputs["Specular IOR Level"].default_value)},
    "materialless_meshes":materialless,
    "missing_external_images":missing_images,
    "linked_libraries":[lib.filepath for lib in bpy.data.libraries],
    "passes_basic_integrity":len(desks)==42 and len(chairs)==62 and len(screens)==2 and all(screens) and len(contents)==6 and len(glass.data.polygons)==44 and not geometry_changes and not materialless and not missing_images and not bpy.data.libraries and max(abs(v) for row in root_obj.matrix_world for v in row if abs(v)>0.0)<=1.000001,
    "limitations":[
        "42 desk/table objects remain schematic; 20 additional chair objects bring the model's chair count to the 62 seats listed by the 2023 guide. This does not reproduce a verified seat-by-seat layout or exact dimensions, and all 62 are not shown at once in a single exterior render.",
        "Dual projection surfaces are source-informed but their size, location and arrangement are not surveyed. Screen content marks and luminous treatment are generic visual cues.",
        "The 44 pane positions and plan-shell geometry match R10 exactly. The approximately 1 m plan-to-shell registration uncertainty remains.",
        "No wall geometry was changed. Upper-floor partitions and circulation remain unverified.",
        "The R11 render-only interior fill light is solely for evidence visibility and is not saved as an installed fixture in the building asset.",
        "The glass material remains a visual legibility estimate; no measured curtain-wall specification was found."
    ]
}
assert report["passes_basic_integrity"], json.dumps(report,indent=2)
out.write_text(json.dumps(report,indent=2),encoding="utf-8")
print(json.dumps(report,indent=2))
