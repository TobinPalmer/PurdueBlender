import bpy, json, hashlib
from pathlib import Path
from collections import Counter
asset = Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\purdue_memorial_union.blend')
out = Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\purdue_memorial_union_independent_grade\fresh_reopen.json')
bpy.ops.wm.open_mainfile(filepath=str(asset))
col=bpy.data.collections.get('Asset_purdue_memorial_union')
if col is None: raise RuntimeError('export collection missing')
objs=list(col.all_objects)
points=[]
for o in objs:
    if o.type not in {'MESH','CURVE','FONT'}: continue
    for c in o.bound_box:
        points.append(o.matrix_world @ __import__('mathutils').Vector(c))
bounds=[[min(v[i] for v in points),max(v[i] for v in points)] for i in range(3)] if points else None
meshes=[o for o in objs if o.type=='MESH']
missing_mats=[o.name for o in meshes if not o.material_slots or all(s.material is None for s in o.material_slots)]
images=[]
for im in bpy.data.images:
    if im.source=='FILE' and im.filepath and not im.packed_file:
        images.append({'name':im.name,'filepath':im.filepath,'exists':Path(bpy.path.abspath(im.filepath)).exists()})
root=bpy.data.objects.get('AssetRoot_purdue_memorial_union')
cameras=[o.name for o in objs if o.type=='CAMERA']
report={
 'asset_path':str(asset),'sha256':hashlib.sha256(asset.read_bytes()).hexdigest(),
 'scene':bpy.context.scene.name,'collection':col.name,'object_count':len(objs),
 'type_counts':dict(Counter(o.type for o in objs)),'mesh_count':len(meshes),
 'root':root.name if root else None,'root_location':list(root.location) if root else None,
 'root_rotation':list(root.rotation_euler) if root else None,'root_scale':list(root.scale) if root else None,
 'bounds_local_m':bounds,'mesh_objects_without_materials':missing_mats,
 'file_images':images,'cameras':cameras,'materials':sorted({s.material.name for o in meshes for s in o.material_slots if s.material}),
 'object_names':[o.name for o in objs],
}
out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='object_names'},indent=2))
