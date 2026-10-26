"""Fresh-process inspection of the FSTW candidate asset."""
import bpy, json
from pathlib import Path
from mathutils import Vector

asset=Path(bpy.data.filepath).resolve()
root=asset.parents[2]
ID="massing_first_street_towers_west_fstw_b6c3bbe"
scene_name="Building_"+ID
collection_name="Asset_"+ID
scene=bpy.data.scenes.get(scene_name)
col=bpy.data.collections.get(collection_name)
if scene is None or col is None: raise RuntimeError("expected FSTW scene/asset collection missing")
wall=col.objects.get("FSTW | GIS perimeter walls, six levels")
if wall is None: raise RuntimeError("GIS wall envelope missing")
ring=[]
for poly in sorted(wall.data.polygons,key=lambda p:p.index):
    vids=list(poly.vertices)
    # Each perimeter quad is created from bottom p, bottom q, top q, top p.
    a=wall.data.vertices[vids[0]].co; b=wall.data.vertices[vids[1]].co
    ring.append([float(a.x),float(a.y)])
points=[tuple(p) for p in ring]
verts=0; faces=0; tris=0; used_materials=set()
for o in col.objects:
    if o.type=="MESH":
        verts+=len(o.data.vertices); faces+=len(o.data.polygons)
        tris+=sum(max(1,len(p.vertices)-2) for p in o.data.polygons)
        used_materials.update(m.name for m in o.data.materials if m)
images=[]
for image in bpy.data.images:
    if image.source=="FILE": images.append({"name":image.name,"filepath":image.filepath,"packed":bool(image.packed_file)})
bb=[tuple(wall.matrix_world@Vector(v)) for v in wall.bound_box]
assetbb=[tuple(o.matrix_world@Vector(v)) for o in col.objects for v in o.bound_box]
doc={
 "asset_id":ID,"asset_path":str(asset),"scene":scene.name,"collection":col.name,
 "collection_object_count":len(col.objects),"collection_mesh_count":sum(o.type=="MESH" for o in col.objects),
 "collection_nonmesh_objects":[{"name":o.name,"type":o.type} for o in col.objects if o.type!="MESH"],
 "total_vertices":verts,"total_faces":faces,"approx_triangles":tris,"material_count":len(used_materials),
 "materials":sorted(used_materials),"external_image_files":images,
 "wall_bounds_xyz":[[min(v[i] for v in bb) for i in range(3)],[max(v[i] for v in bb) for i in range(3)]],
 "asset_bounds_xyz":[[min(v[i] for v in assetbb) for i in range(3)],[max(v[i] for v in assetbb) for i in range(3)]],
 "wall_face_count":len(wall.data.polygons),"wall_bottom_ring_xy":ring,
 "transform_frame":"campus local XYZ meters; asset collection geometry is directly placed in project campus XY frame",
 "render_settings":{"engine":scene.render.engine,"filepath":scene.render.filepath,"resolution":[scene.render.resolution_x,scene.render.resolution_y]},
 "scene_asset_properties":{k:scene[k] for k in scene.keys()}
}
out=asset.parents[2]/"audit"/"first_street_towers_west_fstw_b6c3bbe"/"fresh_open_validation.json"
out.write_text(json.dumps(doc,indent=2),encoding="utf-8")
print(json.dumps({k:doc[k] for k in ["scene","collection","collection_object_count","collection_mesh_count","total_vertices","total_faces","material_count","wall_bounds_xyz","asset_bounds_xyz","wall_face_count","external_image_files"]},indent=2))
