import bpy, json, math, os
from mathutils import Vector

ROOT=r"C:\Users\Tobin\Documents\Blender\PurdueMap"
AUDIT=os.path.join(ROOT,"audit","stewart_fid802")
ASSET=os.path.join(ROOT,"modular","buildings","massing_house_1089875810_8c9b95d.blend")
source=json.load(open(os.path.join(AUDIT,"initial_inspection.json"),encoding="utf-8"))
bpy.ops.wm.open_mainfile(filepath=ASSET)
scene=bpy.data.scenes.get("Building_massing_house_1089875810_8c9b95d")
col=bpy.data.collections.get("Asset_massing_house_1089875810_8c9b95d")
obj=bpy.data.objects.get("House_1089875810")
assert scene and col and obj and obj.type=='MESH'
assert obj.name in col.objects
ring=source["gis_ring_local_xy_m"]
base=[(v.co.x,v.co.y) for v in obj.data.vertices if abs(v.co.z)<1e-5]
errors=[]
for x,y in ring:
    errors.append(min(math.hypot(x-bx,y-by) for bx,by in base))
coords=[]
for o in col.objects:
    if o.type!='MESH': continue
    coords.extend([(o.matrix_world@v.co)[:] for v in o.data.vertices])
bounds=[[min(v[i] for v in coords),max(v[i] for v in coords)] for i in range(3)]
bm=__import__('bmesh').new(); bm.from_mesh(obj.data)
boundary=sum(1 for e in bm.edges if not e.is_manifold); bm.free()
materials=sorted({m.name for o in col.objects if o.type=='MESH' for m in o.data.materials if m})
external_images=[i.filepath for i in bpy.data.images if i.source=='FILE' and i.filepath]
result={"fresh_open":True,"blender_version":bpy.app.version_string,"asset":ASSET,"scene":scene.name,"collection":col.name,"root_object":obj.name,"collection_object_count":len(col.objects),"mesh_object_count":sum(1 for o in col.objects if o.type=='MESH'),"source_feature_id":802,"source_crs":"EPSG:4326 query output; local mapping is approximate campus coordinates","source_vertex_count":len(ring),"wall_base_vertices_at_z0":len(base),"max_nearest_gis_ring_vertex_error_m":max(errors),"mean_nearest_gis_ring_vertex_error_m":sum(errors)/len(errors),"overall_bounds_xyz_m":bounds,"estimated_story_and_roof":"three stories inferred from official house-tour text; 8.7 m eave, 12.15 m main ridge, 13.35 m tower peak; not measured","basement_insert_z_m":-2.45,"nonmanifold_root_shell_edges":boundary,"materials":materials,"external_image_dependencies":external_images,"interior_status":"four separate schematic floor objects and level-specific 3D partitions/furniture/stairs; not as-built"}
assert len(ring)==16 and len(base)>=len(ring) and max(errors)<.001
assert not external_images
json.dump(result,open(os.path.join(AUDIT,"fresh_open_validation.json"),"w",encoding="utf-8"),indent=2)
print(json.dumps(result,indent=2))
