"""Portability and identity check run as a fresh Blender process on the saved file."""
import bpy, hashlib, json
from pathlib import Path
root=Path(__file__).resolve().parents[2]
asset_path=root/"modular/buildings/massing_st_thomas_aquinas_5535390.blend"
audit=Path(__file__).resolve().parent
col=bpy.data.collections.get("Asset_massing_st_thomas_aquinas_5535390")
assert bpy.context.scene.name=="Building_massing_st_thomas_aquinas_5535390"
assert col is not None
objs=list(col.all_objects)
rt=bpy.data.objects.get("AssetRoot_massing_st_thomas_aquinas_5535390")
assert rt and rt.parent is None
assert all(abs(float(x))<1e-7 for x in rt.location)
assert all(abs(float(x))<1e-7 for x in rt.rotation_euler)
assert all(abs(float(x)-1)<1e-7 for x in rt.scale)
deps=bpy.context.evaluated_depsgraph_get();mins=[float("inf")]*3;maxs=[float("-inf")]*3
materialless=[];invalid=[]
for ob in objs:
    if ob.type!="MESH": continue
    if not ob.data.materials: materialless.append(ob.name)
    if any(p.material_index<0 or p.material_index>=len(ob.data.materials) for p in ob.data.polygons): invalid.append(ob.name)
    ev=ob.evaluated_get(deps);me=ev.to_mesh()
    try:
        for v in me.vertices:
            co=ev.matrix_world@v.co
            for i in range(3): mins[i]=min(mins[i],float(co[i]));maxs[i]=max(maxs[i],float(co[i]))
    finally: ev.to_mesh_clear()
missing=[im.filepath for im in bpy.data.images if im.source=="FILE" and im.filepath and not Path(bpy.path.abspath(im.filepath)).exists()]
result={"fresh_process_reopen":True,"asset":str(asset_path),"sha256":hashlib.sha256(asset_path.read_bytes()).hexdigest(),
"scene":bpy.context.scene.name,"export_collection":col.name,"object_count":len(objs),"mesh_count":sum(o.type=="MESH" for o in objs),
"identity_root":True,"bounds_local_axis_major_m":[[mins[i],maxs[i]] for i in range(3)],
"materialless_meshes":materialless,"invalid_material_meshes":invalid,"missing_external_images":missing,
"linked_libraries":[l.filepath for l in bpy.data.libraries],"placement_origin_xy_m":[21.32823749544109,-412.2141452954931]}
assert not materialless and not invalid and not missing and not result["linked_libraries"]
(audit/"independent_reopen_r2.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
print(json.dumps(result,indent=2))
