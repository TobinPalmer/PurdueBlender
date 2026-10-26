"""Validate the reopened Grissom library asset and its assigned footprint."""
import json, math
from pathlib import Path
import bpy

root = Path.cwd()
asset_id = "massing_grissom_hall_01fd0e0"
collection = bpy.data.collections.get("Asset_" + asset_id)
shell = bpy.data.objects.get("Grissom Hall")
assert collection is not None and shell is not None and shell.type == "MESH"
assert all(abs(v) < 1e-8 for v in collection.instance_offset)
assert not shell.modifiers
points=[]
for v in shell.data.vertices:
    if abs(v.co.z) < 1e-4:
        xy=(float(v.co.x),float(v.co.y))
        if not any(math.dist(xy,p)<1e-5 for p in points): points.append(xy)
src=json.loads((root/"audit"/asset_id/"sources"/"official_feature_236.json").read_text(encoding="utf-8"))
feature=src["features"][0]
assert feature["attributes"]["FID"] == 236
source=[]
for lon,lat in feature["geometry"]["rings"][0]:
    xy=((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)),(lat-40.4274)*111040.)
    if not any(math.dist(xy,p)<1e-5 for p in source): source.append(xy)
def directed(a,b): return [min(math.dist(p,q) for q in b) for p in a]
d=directed(points,source)+directed(source,points)
objects=list(collection.objects)
coords=[shell.matrix_world @ v.co for v in shell.data.vertices]
asset_corners=[]
for obj in objects:
    if obj.type!="MESH": continue
    asset_corners.extend(obj.matrix_world @ __import__('mathutils').Vector(corner) for corner in obj.bound_box)
result={
 "reopened_asset":str(root/"modular"/"buildings"/(asset_id+".blend")),
 "collection":collection.name,
 "object_count":len(objects),
 "shell_name":shell.name,
 "shell_bounds_world_m":{"x":[min(v.x for v in coords),max(v.x for v in coords)],"y":[min(v.y for v in coords),max(v.y for v in coords)],"z":[min(v.z for v in coords),max(v.z for v in coords)]},
 "asset_mesh_bounds_world_m":{"x":[min(v.x for v in asset_corners),max(v.x for v in asset_corners)],"y":[min(v.y for v in asset_corners),max(v.y for v in asset_corners)],"z":[min(v.z for v in asset_corners),max(v.z for v in asset_corners)]},
 "footprint_unique_vertex_count":{"shell":len(points),"FID236":len(source)},
 "fid236_bidirectional_nearest_vertex_max_m":max(d),
 "fid236_bidirectional_nearest_vertex_mean_m":sum(d)/len(d),
 "collection_instance_offset":list(collection.instance_offset),
 "shell_modifiers":len(shell.modifiers),
 "external_image_paths":[im.filepath for im in bpy.data.images if im.source=="FILE" and im.filepath and not im.packed_file],
 "all_images_packed_or_generated":all(im.source!="FILE" or not im.filepath or im.packed_file for im in bpy.data.images),
 "material_names":sorted({m.name for o in objects if o.type=="MESH" for m in o.data.materials if m}),
}
assert len(points)==len(source)==22
assert max(d)<0.02
assert abs(result["shell_bounds_world_m"]["z"][1]-14.6304)<0.01
assert result["all_images_packed_or_generated"]
out=root/"audit"/asset_id/"reopened_validation.json"
out.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
print("GRISSOM_REOPENED_VALIDATION",json.dumps(result))
