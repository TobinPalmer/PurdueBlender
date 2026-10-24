"""Reopen and validate the saved R5 Neil source asset; does not save it."""
import bpy, json, os, hashlib
from mathutils import Vector

ROOT = r"C:\Users\Tobin\Documents\Blender\PurdueMap"
ASSET = os.path.join(ROOT, "modular", "buildings", "neil_armstrong_hall.blend")
OUT = os.path.join(ROOT, "audit", "complete_neil_armstrong")
bpy.ops.wm.open_mainfile(filepath=ASSET)
scene = bpy.context.scene
col = bpy.data.collections.get("Asset_neil_armstrong_hall")
root = bpy.data.objects.get("AssetRoot_neil_armstrong_hall")
if scene.name != "Building_neil_armstrong_hall" or col is None or root is None:
    raise RuntimeError("Saved asset identity/collection/root failed")

def world_bounds(objects):
    pts=[]
    for obj in objects:
        if obj.type != "MESH": continue
        for corner in obj.bound_box:
            pts.append(obj.matrix_world @ Vector(corner))
    return [[float(min(p[i] for p in pts)), float(max(p[i] for p in pts))] for i in range(3)]

shell=[o for o in col.objects if o.type=="MESH" and "Wall" in o.name and not o.name.startswith("ARMS_R5")]
new=[o for o in col.objects if o.name.startswith("ARMS_R5_Coarse_LiDAR_")]
if len(new) != 3 or len(col.objects) != 447:
    raise RuntimeError(f"Expected 3 R5 masses and 447 collection objects, got {len(new)} and {len(col.objects)}")

topology=[]
for obj in new:
    # A valid closed envelope should have every edge shared by exactly two faces.
    counts={}
    for poly in obj.data.polygons:
        for ek in poly.edge_keys:
            key=tuple(sorted(ek)); counts[key]=counts.get(key,0)+1
    nonmanifold=sum(1 for n in counts.values() if n != 2)
    if nonmanifold:
        raise RuntimeError(f"{obj.name} contains {nonmanifold} nonmanifold edge keys")
    if obj.parent != root or obj.matrix_parent_inverse != __import__('mathutils').Matrix.Identity(4):
        raise RuntimeError(f"{obj.name} not attached to the identity local root frame")
    if not obj.get("evidence_status", "").startswith("schematic"):
        raise RuntimeError(f"{obj.name} lacks uncertainty label")
    bounds=world_bounds([obj])
    topology.append({"object":obj.name,"vertices":len(obj.data.vertices),"faces":len(obj.data.polygons),
                     "nonmanifold_edge_keys":nonmanifold,"local_bounds_m":bounds,
                     "top_m":float(obj.get("modeled_top_height_m")),"material_slots":[m.name for m in obj.data.materials]})

result={"building_id":"neil_armstrong_hall","revision":"R5","asset_path":"modular/buildings/neil_armstrong_hall.blend",
 "saved_then_reopened_read_only":True,"scene":scene.name,"collection":col.name,"object_count":len(col.objects),
 "asset_root_location":[float(v) for v in root.location],"root_frame_preserved":tuple(root.location)==(0.0,0.0,0.0),
 "existing_shell_wall_bounds_m":world_bounds(shell),"existing_shell_wall_objects":len(shell),
 "new_lidar_mass_objects":topology,"new_objects_parented_to_root":all(o.parent==root for o in new),
 "master_placement_marker":"Not edited. Existing read-only audit: audit/batch3_master/placement_check.json; zero position error, zero rotation, unit scale.",
 "source_alignment":"Official GIS FID 642 and 2018 NDHM were transformed into the manifest local frame, then new masks outside the pre-existing shell rectangle were extruded. Root and all existing objects retained their transforms.",
 "render":"renders_r5/exterior_lidar_wings_r5.png","asset_size_bytes":os.path.getsize(ASSET),
 "asset_sha256":hashlib.sha256(open(ASSET,'rb').read()).hexdigest()}
json.dump(result,open(os.path.join(OUT,"validation_r5.json"),"w",encoding="utf-8"),indent=2)
print(json.dumps(result,indent=2))
