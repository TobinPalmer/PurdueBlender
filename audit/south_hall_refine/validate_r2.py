import bpy, json, os, hashlib
from mathutils import Vector

ROOT=r"C:\Users\Tobin\Documents\Blender\PurdueMap"
ASSET=os.path.join(ROOT,"modular","buildings","south_hall.blend")
OUT=os.path.join(ROOT,"audit","south_hall_refine","validation_r2.json")
bpy.ops.wm.open_mainfile(filepath=ASSET)
asset=bpy.data.collections.get("Asset_south_hall")
ext=bpy.data.collections.get("12_South_Hall_Exterior")
inside=bpy.data.collections.get("13_South_Hall_Interiors")
root=bpy.data.objects.get("AssetRoot_south_hall")
assert asset and ext and inside and root
assert tuple(round(x,6) for x in root.location)==(0.0,0.0,0.0)
assert tuple(round(x,6) for x in root.scale)==(1.0,1.0,1.0)
objs=list(asset.all_objects)
meshes=[o for o in objs if o.type=="MESH"]
missing=[o.name for o in meshes if not o.data.materials or any(m is None for m in o.data.materials)]
assert not missing,missing
external=[im.filepath for im in bpy.data.images if im.source=="FILE" and not im.packed_file]
assert not external,external
pts=[o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
mn=[min(p[i] for p in pts) for i in range(3)]; mx=[max(p[i] for p in pts) for i in range(3)]
base=bpy.data.objects["SouthHall_GIS_GroundFloor_Glass_Podium"]
upper=bpy.data.objects["SouthHall_GIS_Residential_Brick_Envelope"]
fd=json.load(open(os.path.join(ROOT,"audit","south_hall_refine","gis_footprint_r1.json"),encoding="utf-8"))
part=json.load(open(os.path.join(ROOT,"audit","south_hall_refine","gis_partition_r1.json"),encoding="utf-8"))
n=len(fd["local_outline_xy_m"])-1
model_ring=[[round(float(base.data.vertices[i].co.x),6),round(float(base.data.vertices[i].co.y),6)] for i in range(n)]
source_ring=fd["local_outline_xy_m"][:-1]
nu=len(part["residential_outline_xy_local_m"])
upper_ring=[[round(float(upper.data.vertices[i].co.x),6),round(float(upper.data.vertices[i].co.y),6)] for i in range(nu)]
def poly_area(r):
    return abs(sum(r[i][0]*r[(i+1)%len(r)][1]-r[(i+1)%len(r)][0]*r[i][1] for i in range(len(r)))/2)
max_vertex_nearest_error=max(min(((x-u)**2+(y-v)**2)**.5 for u,v in source_ring) for x,y in model_ring)
upper_area=poly_area(upper_ring)
assert abs(upper_area-part["residential_area_m2"])<.01,(upper_area,part["residential_area_m2"])
result={"status":"PASS","asset":ASSET,"blender_version":bpy.app.version_string,"asset_collection":asset.name,"asset_object_count":len(objs),"mesh_count":len(meshes),"exterior_object_count":len(ext.all_objects),"interior_object_count":len(inside.all_objects),"root_location":list(root.location),"root_scale":list(root.scale),"bounds_local_m":[mn,mx],"base_mesh_vertices":len(base.data.vertices),"base_mesh_faces":len(base.data.polygons),"upper_mesh_vertices":len(upper.data.vertices),"upper_mesh_faces":len(upper.data.polygons),"materialless_meshes":missing,"unpacked_external_images":external,"collections":{"asset":asset.name,"exterior":ext.name,"interior":inside.name},"schematic_interior_object_names":[o.name for o in inside.all_objects],"asset_sha256":hashlib.sha256(open(ASSET,"rb").read()).hexdigest()}
result["footprint_registered_overlay"]={"source_fid":528,"simplified_area_m2":fd["outline_metrics"]["simplified_area_m2"],"model_mesh_plan_area_m2":poly_area(model_ring),"model_boundary_xy_local_m":model_ring,"max_model_vertex_to_source_vertex_m":max_vertex_nearest_error,"comparison_note":"asset base mesh was generated from the same simplified Purdue GIS FID 528 boundary; direct boundary match, not an independent survey validation"}
result["massing_partition"]={"residential_upper_shell_plan_area_m2":upper_area,"estimated_low_connector_plan_area_m2":part["connector_area_m2"],"residential_shell_vertex_count":nu,"partition_y_local_m":part["split_y_local_m"],"partition_uncertainty":part["uncertainty"]}
with open(OUT,"w",encoding="utf-8") as f: json.dump(result,f,indent=2)
print("VALIDATION_R2_PASS",len(objs),"objects",len(meshes),"meshes","hash",result["asset_sha256"])
