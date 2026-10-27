import bpy, json, hashlib, os
from mathutils import Vector

ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),"..",".."))
ASSET=os.path.join(ROOT,"modular","buildings","massing_house_301838781_891384f.blend")
OUT=os.path.join(ROOT,"audit","pi_beta_phi","fresh_open_validation.json")
bpy.ops.wm.open_mainfile(filepath=ASSET)
expected_scene="Building_massing_house_301838781_891384f"
expected_collection="Asset_massing_house_301838781_891384f"
scene=bpy.context.scene
collection=bpy.data.collections.get(expected_collection)
images=[]
for image in bpy.data.images:
    images.append({"name":image.name,"filepath":image.filepath,"packed":bool(image.packed_file)})
objects=[]
allpts=[]
for obj in collection.objects if collection else []:
    row={"name":obj.name,"type":obj.type,"location_world":list(obj.matrix_world.translation),"hide_render":obj.hide_render}
    if obj.type=="MESH":
        points=[obj.matrix_world @ v.co for v in obj.data.vertices]
        if points:
            row["bounds_world_local_frame"]=[[min(p[i] for p in points),max(p[i] for p in points)] for i in range(3)]
            allpts.extend(points)
        row["vertices"]=len(obj.data.vertices)
        row["polygons"]=len(obj.data.polygons)
        row["materials"]=[m.name if m else None for m in obj.data.materials]
    objects.append(row)
shell=bpy.data.objects.get("House_301838781")
ring=[]
if shell:
    ring=[list(shell.data.vertices[i].co) for i in range(len(shell.data.vertices)//2)]
    # First half of vertices is the lower GIS ring, in source order.
    ring=[[v[0],v[1]] for v in ring]
bounds=[[min(p[i] for p in allpts),max(p[i] for p in allpts)] for i in range(3)] if allpts else None
with open(ASSET,"rb") as f: sha=hashlib.sha256(f.read()).hexdigest()
report={
 "file":ASSET,"sha256":sha,"blender_version":bpy.app.version_string,
 "scene_name":scene.name,"scene_name_ok":scene.name==expected_scene,
 "expected_collection":expected_collection,"collection_present":collection is not None,
 "stable_source_object_present":shell is not None,"stable_id":"massing_house_301838781_891384f",
 "coordinate_frame":"local geometry centered on official FID 774 centroid; campus XY is -429.57778493112545, -311.88038117902056 m",
 "object_count":len(objects),"mesh_object_count":sum(o["type"]=="MESH" for o in objects),
 "mesh_vertex_count":sum(o.get("vertices",0) for o in objects),"mesh_polygon_count":sum(o.get("polygons",0) for o in objects),
 "local_bounds_all_mesh_objects_m":bounds,"shell_lower_ring_local_xy_m":ring,
 "external_image_dependencies":images,"linked_libraries":[lib.filepath for lib in bpy.data.libraries],
 "has_portico":any(o["name"].startswith("PiPhi_portico_column_") for o in objects),
 "has_interior":any(o["name"]=="PiPhi_interior_floor_1" for o in objects),
 "exterior_preview_exists":os.path.exists(os.path.join(ROOT,"audit","pi_beta_phi","view_front.png")),
 "three_quarter_preview_exists":os.path.exists(os.path.join(ROOT,"audit","pi_beta_phi","view_three_quarter.png")),
 "interior_cutaway_preview_exists":os.path.exists(os.path.join(ROOT,"audit","pi_beta_phi","view_interior_cutaway.png")),
 "pass":scene.name==expected_scene and collection is not None and shell is not None and not bpy.data.libraries and not images and len(objects)>=100,
 "notes":["The building library intentionally contains local coordinates; master Placement marker and shared manifest require Tobin integration.","Story height, parapet/roof form, floor plan and room/furniture arrangement remain estimated or conceptual."]
}
with open(OUT,"w",encoding="utf-8") as f: json.dump(report,f,indent=2)
print(json.dumps({k:v for k,v in report.items() if k!="shell_lower_ring_local_xy_m"},indent=2))
