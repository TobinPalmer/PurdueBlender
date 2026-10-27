"""Fresh-process validation for the standalone YONG library."""
import bpy, json, math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).with_name("fresh_open_validation.json")
GIS=json.loads((Path(__file__).parent/"purdue_gis_yong_fid70.json").read_text(encoding="utf-8"))
feature=GIS["features"][0]
ring=feature["geometry"]["rings"][0]
if ring[0]==ring[-1]: ring=ring[:-1]
expected=[((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)),
           (lat-40.4274)*111040.0) for lon,lat in ring]
coll=bpy.data.collections.get("Asset_massing_young_hall_yong_cae1b95")
shell=bpy.data.objects.get("Young Hall (YONG)")
errors=[]
if coll is None: errors.append("stable export collection missing")
if shell is None: errors.append("stable building object missing")
actual=[]
if shell:
    actual=[((shell.matrix_world @ v.co).x,(shell.matrix_world @ v.co).y)
            for v in shell.data.vertices if abs((shell.matrix_world @ v.co).z)<1e-5]
    # Blender mesh coordinates are stored at single-precision tolerance.
    if len(actual)!=len(expected): errors.append(f"bottom-ring count differs: {len(actual)} vs {len(expected)}")
    vertex_errors=[math.hypot(a[0]-e[0],a[1]-e[1]) for a,e in zip(actual,expected)]
    if len(actual)==len(expected) and max(vertex_errors,default=0)>0.01:
        errors.append("bottom-ring vertices differ from projected GIS ring by more than 0.01 m")
    if shell.modifiers: errors.append("shell has unapplied or unevaluated modifiers")
    if shell.parent: errors.append("shell unexpectedly parented")

scene=bpy.context.scene
members=list(coll.objects) if coll else []
mesh_objects=[o for o in members if o.type=="MESH"]
all_world=[]
deps=bpy.context.evaluated_depsgraph_get()
for o in members:
    if o.type=="MESH":
        ev=o.evaluated_get(deps); me=ev.to_mesh()
        all_world.extend([ev.matrix_world @ v.co for v in me.vertices])
        ev.to_mesh_clear()
for block in bpy.data.images:
    if block.filepath and block.source=="FILE":
        p=bpy.path.abspath(block.filepath, library=block.library)
        if not Path(p).exists(): errors.append("missing external image: "+p)
shell_world=[shell.matrix_world@v.co for v in shell.data.vertices] if shell else []
def bounds(points):
    return [[min(p[i] for p in points),max(p[i] for p in points)] for i in range(3)] if points else None
shell_bounds=bounds(shell_world)
record={
 "status":"PASS" if not errors else "FAIL",
 "asset":str(ROOT/"modular/buildings/massing_young_hall_yong_cae1b95.blend"),
 "blender_version":bpy.app.version_string,
 "scene":scene.name,
 "export_collection":"Asset_massing_young_hall_yong_cae1b95" if coll else None,
 "collection_object_count":len(members),
 "mesh_object_count":len(mesh_objects),
 "object_types":{t:sum(o.type==t for o in members) for t in sorted(set(o.type for o in members))},
 "shell_world_bounds_m":shell_bounds,
 "gis_world_bounds_m":[[min(p[i] for p in expected),max(p[i] for p in expected)] for i in range(2)],
 "gis_ring_vertices":len(expected),
 "shell_base_vertices":len(actual),
 "gis_ring_max_vertex_error_m":max(vertex_errors,default=None),
 "gis_ring_match":"PASS" if len(actual)==len(expected) and max(vertex_errors,default=0)<=0.01 else "FAIL",
 "collection_world_bounds_m":bounds(all_world),
 "shell_materials":[m.name for m in shell.data.materials] if shell else [],
 "shell_polygon_count":len(shell.data.polygons) if shell else None,
 "external_file_dependencies_checked":True,
 "errors":errors
}
OUT.write_text(json.dumps(record,indent=2),encoding="utf-8")
print(json.dumps(record,indent=2))
