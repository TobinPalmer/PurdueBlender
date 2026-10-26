import bpy, hashlib, json
from pathlib import Path
root=Path(__file__).resolve().parents[2]
asset=root/'modular/buildings/rawls_hall.blend'
out=root/'audit/batch4_rawls/asset_bounds_r11.json'
coll=bpy.data.collections.get('Asset_rawls_hall')
if not coll: raise RuntimeError('Asset_rawls_hall missing')
dg=bpy.context.evaluated_depsgraph_get()
pts=[]; rows=[]
for obj in coll.all_objects:
    if obj.type!='MESH': continue
    ev=obj.evaluated_get(dg); me=ev.to_mesh()
    try:
        if not me.vertices: continue
        world=[ev.matrix_world@v.co for v in me.vertices]
        pts.extend(world)
        bb=[[min(p[i] for p in world),max(p[i] for p in world)] for i in range(3)]
        if any(max(abs(x) for x in axis)>120 for axis in bb): rows.append({'object':obj.name,'bounds_local_m':bb})
    finally: ev.to_mesh_clear()
if not pts: raise RuntimeError('No evaluated mesh vertices')
bounds=[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)]
report={'asset':str(asset),'sha256':hashlib.sha256(asset.read_bytes()).hexdigest(),'collection':coll.name,'object_count':len(coll.all_objects),'mesh_count':sum(o.type=='MESH' for o in coll.all_objects),'bounds_local_axis_major_m':bounds,'mesh_objects_outside_120m':rows,'identity_root':{'location':list(bpy.data.objects['AssetRoot_rawls_hall'].location),'rotation':list(bpy.data.objects['AssetRoot_rawls_hall'].rotation_euler),'scale':list(bpy.data.objects['AssetRoot_rawls_hall'].scale)},'method':'Fresh standalone Blender 5.2.3 reopen; evaluated vertices of all meshes in exported collection using object world transforms.'}
out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2))
