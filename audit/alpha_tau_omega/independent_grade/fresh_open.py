import bpy, json, hashlib
from pathlib import Path
asset = Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\massing_house_301840870_c45a5f4.blend')
report = Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\alpha_tau_omega\independent_grade\fresh_open.json')
bpy.ops.wm.open_mainfile(filepath=str(asset))
scene=bpy.data.scenes.get('Building_massing_house_301840870_c45a5f4')
col=bpy.data.collections.get('Asset_massing_house_301840870_c45a5f4')
root=bpy.data.objects.get('House_301840870')
assert scene and col and root and root.name in col.objects
objects=list(col.objects)
deps=bpy.context.evaluated_depsgraph_get(); coords=[]
for ob in objects:
    ev=ob.evaluated_get(deps)
    if ev.type=='MESH':
        me=ev.to_mesh()
        coords += [ob.matrix_world@v.co for v in me.vertices]
        ev.to_mesh_clear()
external=[]
for im in bpy.data.images:
    if im.source=='FILE' and im.filepath and not im.packed_file:
        p=Path(bpy.path.abspath(im.filepath)); external.append({'path':im.filepath,'exists':p.exists()})
materials=sorted({m.name for o in objects if hasattr(o.data,'materials') for m in o.data.materials if m})
result={'fresh_open':True,'sha256':hashlib.sha256(asset.read_bytes()).hexdigest().upper(),'scene':scene.name,'collection':col.name,'object_count':len(objects),'root':root.name,'root_transform':{'location':list(root.location),'rotation':list(root.rotation_euler),'scale':list(root.scale)},'bounds_xyz_m':[[min(c[i] for c in coords),max(c[i] for c in coords)] for i in range(3)],'materials':materials,'image_dependencies':external,'all_materials_nodes':all(m.use_nodes for m in bpy.data.materials),'objects_without_materials':[o.name for o in objects if o.type=='MESH' and not o.data.materials]}
report.write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))

