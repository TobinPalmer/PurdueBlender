"""Reopen and validate the saved R6 Neil source without writing the blend."""
import bpy, json, hashlib, os
from mathutils import Vector, Matrix

ROOT=r"C:\Users\Tobin\Documents\Blender\PurdueMap"
ASSET=os.path.join(ROOT,"modular","buildings","neil_armstrong_hall.blend")
OUT=os.path.join(ROOT,"audit","complete_neil_armstrong")
with open(os.path.join(OUT,"validation_r5.json"),encoding="utf-8") as f: r5=json.load(f)
bpy.ops.wm.open_mainfile(filepath=ASSET)
scene=bpy.context.scene
col=bpy.data.collections.get("Asset_neil_armstrong_hall")
root=bpy.data.objects.get("AssetRoot_neil_armstrong_hall")
assert scene.name=="Building_neil_armstrong_hall" and col and root
assert len(col.objects)==449, f"Expected 449 source objects, found {len(col.objects)}"
assert tuple(root.location)==(0.0,0.0,0.0)

def bounds(objects):
    pts=[o.matrix_world@Vector(c) for o in objects if o.type=="MESH" for c in o.bound_box]
    return [[float(min(p[i] for p in pts)),float(max(p[i] for p in pts))] for i in range(3)]

shell=[o for o in col.objects if o.type=="MESH" and "Wall" in o.name and not o.name.startswith("ARMS_R5")]
shell_bounds=bounds(shell)
expected=r5["existing_shell_wall_bounds_m"]
assert len(shell)==r5["existing_shell_wall_objects"]
assert all(abs(shell_bounds[a][b]-expected[a][b])<1e-5 for a in range(3) for b in range(2)), shell_bounds

lidar=[bpy.data.objects.get(n) for n in (
    "ARMS_R5_Coarse_LiDAR_wing_low","ARMS_R5_Coarse_LiDAR_wing_mid","ARMS_R5_Coarse_LiDAR_roof_high")]
assert all(o and o.parent==root and o.matrix_parent_inverse==Matrix.Identity(4) for o in lidar)
assert [round(float(o.get("modeled_top_height_m")),2) for o in lidar]==[15.78,19.48,21.55]
glass=bpy.data.objects["ARMS_R6_North_Clerestory_Glass"]
mullions=bpy.data.objects["ARMS_R6_North_Clerestory_Mullions"]
assert glass.parent==root and mullions.parent==root
assert len(glass.data.vertices)==22*8 and len(mullions.data.vertices)==25*8
assert "not be read as a registered elevation" in glass.get("registration_uncertainty","")

roof=lidar[-1]
acm_slot=next(i for i,m in enumerate(roof.data.materials) if m and m.name=="ARMS_R6_Mayflower_Red_ACM")
up_faces=[p for p in roof.data.polygons if p.normal.z>0.85]
assert len(up_faces)>0 and all(p.material_index==acm_slot for p in up_faces)
assert "not registered" in roof.get("roof_finish_note","")

result={
  "building_id":"neil_armstrong_hall","revision":"R6","asset_path":"modular/buildings/neil_armstrong_hall.blend",
  "saved_then_reopened_read_only":True,"scene":scene.name,"collection":col.name,"object_count":len(col.objects),
  "root_location_m":[float(v) for v in root.location],"existing_shell_wall_count":len(shell),
  "existing_shell_wall_bounds_m":shell_bounds,"r5_lidar_envelopes_preserved":True,
  "lidar_envelopes":[{"name":o.name,"top_m":float(o.get("modeled_top_height_m")),"bounds_m":bounds([o])} for o in lidar],
  "r6_facade":{"glass_object":glass.name,"glass_panel_count":22,"glass_bounds_m":bounds([glass]),"mullion_object":mullions.name,"mullion_piece_count":25,"schematic_registration_uncertainty":glass.get("registration_uncertainty")},
  "r6_roof":{"upward_facets_with_acm":len(up_faces),"material":"ARMS_R6_Mayflower_Red_ACM","plan_boundary_uncertainty":roof.get("roof_finish_note")},
  "master_marker_read_only_audit":"audit/batch3_master/placement_check.json (Neil marker at [-109.0,400.1893310546875,0], zero position error, zero rotation, unit scale; unchanged)",
  "renders":["renders_r6/exterior_northwest_r6.png","renders_r6/atrium_bridges_section_r6.png"],
  "asset_size_bytes":os.path.getsize(ASSET),"asset_sha256":hashlib.sha256(open(ASSET,"rb").read()).hexdigest()
}
with open(os.path.join(OUT,"validation_r6.json"),"w",encoding="utf-8") as f: json.dump(result,f,indent=2)
print(json.dumps(result,indent=2))
