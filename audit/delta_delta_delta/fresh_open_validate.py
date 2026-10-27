"""Fresh-process validation for the Delta Delta Delta building library."""
import bpy, json, math, os, hashlib
from mathutils import Vector

ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),"..",".."))
ASSET_ID="massing_house_301841333_affe21e"
ASSET_PATH=os.path.join(ROOT,"modular","buildings",ASSET_ID+".blend")
OUT=os.path.join(ROOT,"audit","delta_delta_delta","fresh_open_validation.json")
bpy.ops.wm.open_mainfile(filepath=ASSET_PATH)
scene=bpy.data.scenes.get("Building_"+ASSET_ID)
coll=bpy.data.collections.get("Asset_"+ASSET_ID)
if scene is None or coll is None:
    raise RuntimeError("Expected scene or exported collection is absent")
mesh_objects=[o for o in coll.objects if o.type=="MESH"]
vertices=[]
for obj in mesh_objects:
    deps=bpy.context.evaluated_depsgraph_get()
    ev=obj.evaluated_get(deps)
    for v in ev.data.vertices:
        vertices.append(obj.matrix_world @ v.co)
if not vertices:
    raise RuntimeError("Exported collection has no mesh geometry")
mins=[min(v[i] for v in vertices) for i in range(3)]
maxs=[max(v[i] for v in vertices) for i in range(3)]
external_images=[img.filepath for img in bpy.data.images if img.source=="FILE" and not img.packed_file]
linked_libraries=[lib.filepath for lib in bpy.data.libraries]
materials=sorted({m.name for o in mesh_objects for m in o.data.materials if m})
root=bpy.data.objects.get("AssetRoot_"+ASSET_ID)
footprint_obj=bpy.data.objects.get("DDD_Foundation_Base")
outline=[list(v.co[:2]) for v in footprint_obj.data.vertices if abs(v.co.z)<1e-6] if footprint_obj else []
result={
  "asset_path":os.path.relpath(ASSET_PATH,ROOT).replace("\\","/"),
  "sha256":hashlib.sha256(open(ASSET_PATH,"rb").read()).hexdigest(),
  "blender_version":".".join(map(str,bpy.app.version)),
  "scene":scene.name,
  "collection":coll.name,
  "collection_object_count":len(coll.objects),
  "mesh_object_count":len(mesh_objects),
  "evaluated_local_bounds_m":[mins,maxs],
  "expected_xy_placement_origin_m":list(root["placement_origin_xy_m"]),
  "local_coordinates":bool(root["local_coordinates"]),
  "foundation_outline_vertex_count":len(outline),
  "foundation_outline_local_m":outline,
  "external_unpacked_images":external_images,
  "linked_libraries":linked_libraries,
  "materials":materials,
  "errors":[],
  "status":"PASS"
}
if len(coll.objects)<800: result["errors"].append("unexpectedly low collection object count")
if external_images: result["errors"].append("unpacked external images found")
if linked_libraries: result["errors"].append("linked library dependencies found")
if not result["local_coordinates"]: result["errors"].append("asset root lacks local-coordinate marker")
if result["errors"]: result["status"]="FAIL"
with open(OUT,"w",encoding="utf-8") as f: json.dump(result,f,indent=2)
print(json.dumps(result,indent=2))
