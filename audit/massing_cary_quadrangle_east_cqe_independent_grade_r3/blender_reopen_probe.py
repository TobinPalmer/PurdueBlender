import bpy, hashlib, json, math
from pathlib import Path

ROOT = Path(r"C:\Users\gotse\Documents\Codex\2026-10-25\github-plugin-github-openai-curated-remote\outputs\PurdueBlender")
ASSET = ROOT / "modular/buildings/massing_cary_quadrangle_east_cqe_230c813.blend"
OUT = ROOT / "audit/massing_cary_quadrangle_east_cqe_independent_grade_r3/blender_probe.json"
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
scene = bpy.context.scene
asset_id = "massing_cary_quadrangle_east_cqe_230c813"
coll_name = "Asset_" + asset_id
coll = bpy.data.collections.get(coll_name)
assert coll is not None, f"missing expected collection {coll_name}"
assert scene.name == "Building_" + asset_id
rows=[]
all_mins=[float("inf")]*3
all_maxs=[float("-inf")]*3
identity=True
for ob in sorted(coll.objects, key=lambda o:o.name):
    bb=[ob.matrix_world @ __import__('mathutils').Vector(corner) for corner in ob.bound_box]
    mins=[min(v[i] for v in bb) for i in range(3)]
    maxs=[max(v[i] for v in bb) for i in range(3)]
    for i in range(3): all_mins[i]=min(all_mins[i],mins[i]); all_maxs[i]=max(all_maxs[i],maxs[i])
    is_identity=(all(abs(x)<1e-7 for x in ob.location) and all(abs(x)<1e-7 for x in ob.rotation_euler) and all(abs(x-1)<1e-7 for x in ob.scale))
    identity &= is_identity
    row={"name":ob.name,"type":ob.type,"location":list(ob.location),"rotation":list(ob.rotation_euler),"scale":list(ob.scale),"bounds_world_xyz":[[mins[i],maxs[i]] for i in range(3)],"dimensions":list(ob.dimensions),"modifier_count":len(ob.modifiers),"materials":[m.name if m else None for m in ob.data.materials] if ob.type=="MESH" else []}
    if ob.type=="MESH":
        row["vertices"]=len(ob.data.vertices); row["polygons"]=len(ob.data.polygons)
        if ob.name=="CQE_Stone_Foundation_Shell":
            zs=[(ob.matrix_world @ v.co).z for v in ob.data.vertices]
            zmin=min(zs)
            row["bottom_outline_xy"]=[[round((ob.matrix_world@v.co).x,6),round((ob.matrix_world@v.co).y,6)] for v in ob.data.vertices if abs((ob.matrix_world@v.co).z-zmin)<1e-6]
    rows.append(row)
out={"asset_path":"modular/buildings/massing_cary_quadrangle_east_cqe_230c813.blend","asset_id":asset_id,"scene":scene.name,"collection":coll.name,"blender_version":bpy.app.version_string,"collection_asset_id":coll.get("asset_id"),"objects":len(coll.objects),"mesh_objects":sum(o.type=="MESH" for o in coll.objects),"bounds_world_m_xyz":[[all_mins[i],all_maxs[i]] for i in range(3)],"all_object_transforms_identity":identity,"external_libraries":[lib.filepath for lib in bpy.data.libraries if lib.filepath],"other_collection_names":[c.name for c in bpy.data.collections if c!=coll],"blend_sha256":hashlib.sha256(ASSET.read_bytes()).hexdigest(),"object_rows":rows}
OUT.write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8")
print(json.dumps({k:v for k,v in out.items() if k!="object_rows"},indent=2))
