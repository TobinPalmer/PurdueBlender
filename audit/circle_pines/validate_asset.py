"""Run inside Blender after the asset has been saved to reopen and inspect it."""
import bpy, json, math
from pathlib import Path

root=Path(__file__).resolve().parents[2]
asset_path=root/"modular/buildings/massing_house_301841609_c6c9ac4.blend"
source_path=root/"audit/circle_pines/sources/purdue_gis_fid761_raw.json"
bpy.ops.wm.open_mainfile(filepath=str(asset_path))
collection=bpy.data.collections.get("Asset_massing_house_301841609_c6c9ac4")
assert collection is not None
objects=list(collection.objects)
assert len(objects)==1, f"Expected one asset object; found {len(objects)}"
obj=objects[0]
assert obj.name=="House_301841609" and obj.type=="MESH"
assert tuple(round(v,6) for v in obj.location)==(0.0,0.0,0.0)
assert tuple(round(v,6) for v in obj.rotation_euler)==(0.0,0.0,0.0)
assert tuple(round(v,6) for v in obj.scale)==(1.0,1.0,1.0)
assert len(obj.modifiers)==0
feature=json.loads(source_path.read_text(encoding="utf-8-sig"))["features"][0]
ring=feature["geometry"]["rings"][0][:-1]
sx=111412.84*math.cos(math.radians(40.4274));sy=111040.0
pts=[((lon+86.9137)*sx,(lat-40.4274)*sy) for lon,lat in ring]
source_bounds=[[min(x for x,y in pts),max(x for x,y in pts)],[min(y for x,y in pts),max(y for x,y in pts)],[0.0,7.3]]
coords=[obj.matrix_world@v.co for v in obj.data.vertices]
bounds=[[min(v[i] for v in coords),max(v[i] for v in coords)] for i in range(3)]
base=[v for v in coords if abs(v.z)<0.001]
structural_xy=[[min(v[i] for v in base),max(v[i] for v in base)] for i in range(2)]
for i in range(2):
    for j in range(2): assert abs(structural_xy[i][j]-source_bounds[i][j])<0.002
assert abs(bounds[2][0]-0)<0.002 and abs(bounds[2][1]-7.3)<0.002
assert all(img is None or not img.filepath for img in bpy.data.images)
result={
 "status":"pass","asset":str(asset_path),"scene":bpy.context.scene.name,
 "collection":collection.name,"objects":[o.name for o in objects],
 "mesh_vertices":len(obj.data.vertices),"mesh_faces":len(obj.data.polygons),
 "modifiers":len(obj.modifiers),"identity_transform":True,
 "source_gis_unique_vertices":len(ring),"source_converted_bounds_m":source_bounds,
 "reopened_asset_bounds_m":bounds,"structural_base_xy_bounds_m":structural_xy,
 "xy_bound_max_error_m":max(abs(structural_xy[i][j]-source_bounds[i][j]) for i in range(2) for j in range(2)),
 "height_m":{"value":7.3,"status":"estimated"},"external_image_dependencies":0,
 "checks":["reopened saved blend","expected scene/collection/object","single mesh object","identity transform","GIS footprint bounds","estimated height extent","no modifiers","no external image dependencies"]
}
(root/"audit/circle_pines/reopen_validation.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
print(json.dumps(result,indent=2))
