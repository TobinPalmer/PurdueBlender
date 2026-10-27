"""Run from Blender with the Windsor asset opened; capture fresh-open facts."""
import bpy, json, os
from mathutils import Vector

root=os.path.abspath(os.path.join(os.path.dirname(__file__),"..",".."))
collection=bpy.data.collections.get("Asset_massing_windsor_halls_80aeb51")
if collection is None: raise RuntimeError("Stable Windsor asset collection is missing")
mesh_objects=[o for o in collection.objects if o.type=="MESH"]
all_points=[o.matrix_world @ Vector(corner) for o in mesh_objects for corner in o.bound_box]
shells={}
placement=( -617.8, -96.6 )
for fid in (63,64,65,66):
    obj=next((o for o in mesh_objects if f"FID {fid}) | structural footprint shell" in o.name),None)
    if obj is None: raise RuntimeError(f"Missing GIS shell for FID {fid}")
    bottom=obj.data.polygons[0]
    shells[str(fid)]=[[round((obj.matrix_world @ obj.data.vertices[i].co).x,7),
                       round((obj.matrix_world @ obj.data.vertices[i].co).y,7)] for i in bottom.vertices]
report={
    "fresh_open":True,
    "asset":"modular/buildings/massing_windsor_halls_80aeb51.blend",
    "scene":bpy.context.scene.name,
    "collection":collection.name,
    "collection_object_count":len(collection.objects),
    "mesh_object_count":len(mesh_objects),
    "mesh_vertex_count":sum(len(o.data.vertices) for o in mesh_objects),
    "mesh_face_count":sum(len(o.data.polygons) for o in mesh_objects),
    "material_count":len({m.name for o in mesh_objects for m in o.data.materials}),
    "materials":sorted({m.name for o in mesh_objects for m in o.data.materials}),
    "bounds_m":{"xmin":min(p.x for p in all_points),"xmax":max(p.x for p in all_points),
                 "ymin":min(p.y for p in all_points),"ymax":max(p.y for p in all_points),
                 "zmin":min(p.z for p in all_points),"zmax":max(p.z for p in all_points)},
    "structural_shell_xy":shells,
    "coordinate_system":"local building meters; X east, Y north, Z up",
    "placement_origin_campus_xy_m":list(placement),
    "placement_marker_object":next((o.name for o in collection.objects if o.type=="EMPTY" and o.get("asset_id")=="massing_windsor_halls_80aeb51"),None),
}
out=os.path.join(os.path.dirname(__file__),"fresh_open_raw.json")
with open(out,"w",encoding="utf-8") as f: json.dump(report,f,indent=2)
print("FRESH_OPEN_VALIDATED",out)
