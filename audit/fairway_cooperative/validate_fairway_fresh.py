import bpy, json, hashlib, os, math

root=os.path.abspath(os.path.join(os.path.dirname(__file__),"..",".."))
asset=os.path.join(root,"modular","buildings","massing_fairway_cooperative_2101b77.blend")
report_path=os.path.join(os.path.dirname(__file__),"fresh_open_validation.json")
expected_scene="Building_massing_fairway_cooperative_2101b77"
expected_collection="Asset_massing_fairway_cooperative_2101b77"
scene=bpy.context.scene
collection=bpy.data.collections.get(expected_collection)
assert scene.name==expected_scene, (scene.name,expected_scene)
assert collection is not None
assert collection.name in [c.name for c in scene.collection.children_recursive]
objects=list(collection.objects)
assert len(objects)>100
assert all(o.type in {"MESH","FONT","CURVE","EMPTY","LIGHT","CAMERA"} for o in objects)
world_pts=[]
for obj in objects:
    if obj.type!="MESH": continue
    for v in obj.bound_box:
        world_pts.append(obj.matrix_world @ bpy.mathutils.Vector(v) if hasattr(bpy,"mathutils") else obj.matrix_world @ __import__('mathutils').Vector(v))
lo=[min(p[i] for p in world_pts) for i in range(3)]
hi=[max(p[i] for p in world_pts) for i in range(3)]
images=[]
for image in bpy.data.images:
    if image.source=="FILE" and image.filepath and not image.packed_file:
        images.append(image.filepath)
libraries=[lib.filepath for lib in bpy.data.libraries]
material_count=len({m.name for o in objects if o.type=="MESH" for m in o.data.materials if m})
sha=hashlib.sha256(open(asset,"rb").read()).hexdigest()
result={"status":"PASS","fresh_process_opened":True,"blender_version":bpy.app.version_string,
 "scene":scene.name,"collection":collection.name,"asset_objects":len(objects),
 "mesh_objects":sum(o.type=="MESH" for o in objects),"materials":material_count,
 "bounds_world_m":[lo,hi],"linked_libraries":libraries,"unpacked_external_images":images,
 "candidate_sha256":sha,"file_bytes":os.path.getsize(asset)}
assert not libraries, libraries
assert not images, images
assert result["mesh_objects"]>100
with open(report_path,"w",encoding="utf-8") as f: json.dump(result,f,indent=2)
print("FAIRWAY_FRESH_OPEN_PASS",json.dumps(result))
