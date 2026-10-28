import bpy, bmesh, json, os, hashlib
from mathutils import Vector

ROOT=r"C:\Users\Tobin\Documents\Blender\PurdueMap"
AUDIT=os.path.join(ROOT,"audit","circle_pines_fid761")
ASSET=os.path.join(ROOT,"modular","buildings","massing_house_301841609_c6c9ac4.blend")
GIS=json.load(open(os.path.join(AUDIT,"initial_inspection.json"),encoding="utf-8"))
bpy.ops.wm.open_mainfile(filepath=ASSET)
scene=bpy.data.scenes.get("Building_massing_house_301841609_c6c9ac4") or bpy.context.scene
obj=bpy.data.objects.get("House_301841609")
assert obj is not None and obj.type=="MESH"
assert obj.name in bpy.data.collections["Asset_massing_house_301841609_c6c9ac4"].objects
ring=GIS["gis_ring_xy_local_m"]
if ring[0]==ring[-1]: ring=ring[:-1]
base_match=max(max(abs(obj.data.vertices[i].co.x-ring[i][0]),abs(obj.data.vertices[i].co.y-ring[i][1]),abs(obj.data.vertices[i].co.z)) for i in range(len(ring)))
bm=bmesh.new(); bm.from_mesh(obj.data)
print("wall-base vertex comparison max error",base_match)
nonmanifold=sum(not e.is_manifold for e in bm.edges)
boundary=sum(e.is_boundary for e in bm.edges)
lo=[min(v.co[i] for v in obj.data.vertices) for i in range(3)]
hi=[max(v.co[i] for v in obj.data.vertices) for i in range(3)]
result={"fresh_open":True,"blender_version":bpy.app.version_string,"file":ASSET,"scene":scene.name,
        "collection":"Asset_massing_house_301841609_c6c9ac4","object":obj.name,"object_count":len(scene.objects),
        "vertex_count":len(obj.data.vertices),"face_count":len(obj.data.polygons),"materials":[m.name for m in obj.data.materials],
        "bounds_local_m":{"min":lo,"max":hi},"source_ring_vertex_count":len(ring),
        "max_error_gis_wall_base_xy_m":base_match,"nonmanifold_edges":nonmanifold,"boundary_edges":boundary,
        "height_status":"estimated 5.75 m total from two visible window bands; not measured; GIS NUM_LEVELS=1 conflict retained",
        "facade_status":"one camera-facing facade interpreted from April 2026 Street View; other elevations unverified",
        "interior_status":"one-level schematic 3D floors, partitions, circulation, step run and furnishing inserts; not as-built; upper interior unverified"}
bm.free()
assert base_match<1e-4
assert len(scene.objects)==1
assert abs(hi[2]-5.75)<1e-6
json.dump(result,open(os.path.join(AUDIT,"fresh_open_validation.json"),"w",encoding="utf-8"),indent=2)
print(json.dumps(result,indent=2))
