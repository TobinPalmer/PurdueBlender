"""Reopen and geometrically verify the Dudley library against GIS evidence."""
from pathlib import Path
import json, math, bpy

ROOT=Path(__file__).resolve().parents[2]
asset=ROOT/"modular"/"buildings"/"dudley_hall.blend"
gis=json.load(open(ROOT/"audit"/"dudley_hall"/"sources"/"purdue_gis_fid432_dudley_hall.json",encoding="utf-8"))["feature"]
bpy.ops.wm.open_mainfile(filepath=str(asset))
collection=bpy.data.collections.get("Asset_dudley_hall")
shell=bpy.data.objects.get("dudley_hall")
if not collection or not shell or shell.type!="MESH":
    raise RuntimeError("Expected Dudley export collection or shell missing")
shell_points={(round(v.co.x,4),round(v.co.y,4)) for v in shell.data.vertices if abs(v.co.z)<1e-4}
gis_points=[tuple(p) for p in gis["rings_xy_m"][0]]
nearest=[min(math.dist(p,q) for q in shell_points) for p in gis_points]
shell_xy=list(shell_points)
reverse=[min(math.dist(p,q) for q in gis_points) for p in shell_xy]
all_meshes=[o for o in collection.objects if o.type=="MESH"]
detail=[o for o in all_meshes if o.name.startswith("DUDLEY_DETAIL_")]
bounds=[]
for axis in range(3):
    vals=[o.matrix_world @ v.co for o in all_meshes for v in o.data.vertices]
    bounds.append([round(min(v[axis] for v in vals),4),round(max(v[axis] for v in vals),4)])
result={
 "asset_path":"modular/buildings/dudley_hall.blend","collection":"Asset_dudley_hall",
 "reopened_in_blender":bpy.app.version_string,"mesh_object_count":len(all_meshes),
 "detail_mesh_object_count":len(detail),"detail_mesh_faces":sum(len(o.data.polygons) for o in detail),
 "gis_feature_id":gis["fid"],"gis_code":gis["code"],
 "source_polygon_vertex_count":len(gis_points),"shell_lower_ring_unique_vertex_count":len(shell_points),
 "bounds_xyz_m":bounds,"gis_to_shell_nearest_max_m":round(max(nearest),4),
 "shell_to_gis_nearest_max_m":round(max(reverse),4),
 "collection_world_location":list(collection.instance_offset),
 "assessment":"Footprint compares only the official XY polygon and shell perimeter. Height, facade bay positions, glass extents, and coping are estimated from architect photographs and published floor count."
}
out=ROOT/"audit"/"dudley_hall"/"asset_validation.json"
out.write_text(json.dumps(result,indent=2),encoding="utf-8")
print(json.dumps(result,indent=2))
