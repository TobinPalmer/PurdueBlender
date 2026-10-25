import bpy, json, math, os
from pathlib import Path
blend=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\owen_hall.blend'
out=r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\owen_hall_independent_grade\asset_inspection.json'
bpy.ops.wm.open_mainfile(filepath=blend)
col=bpy.data.collections.get('Asset_owen_hall')
assert col is not None
objs=list(col.objects)
root=bpy.data.objects.get('AssetRoot_owen_hall')
dg=bpy.context.evaluated_depsgraph_get()
all_pts=[]; struct=[]; image_paths=[]
for o in objs:
 if o.type!='MESH': continue
 eo=o.evaluated_get(dg); me=eo.to_mesh()
 for v in me.vertices:
  p=o.matrix_world @ v.co
  all_pts.append((p.x,p.y,p.z))
 eo.to_mesh_clear()
 if 'Limestone_Base' in o.name or '_GF_Wall_' in o.name:
  coords=[o.matrix_world @ v.co for v in o.data.vertices]
  if coords:
   struct.append({'name':o.name,'bounds':[[min(p.x for p in coords),max(p.x for p in coords)],[min(p.y for p in coords),max(p.y for p in coords)],[min(p.z for p in coords),max(p.z for p in coords)]]})
for im in bpy.data.images:
 if im.source=='FILE': image_paths.append({'name':im.name,'filepath':im.filepath,'packed':im.packed_file is not None})
for lib in bpy.data.libraries:
 image_paths.append({'library':lib.filepath})
metrics={
 'blend_path':blend,'scene_names':[s.name for s in bpy.data.scenes], 'collection_exists':True,
 'collection_name':col.name,'collection_object_count':len(objs),'types':{t:sum(o.type==t for o in objs) for t in sorted({o.type for o in objs})},
 'root_location':[root.location.x,root.location.y,root.location.z] if root else None,
 'root_world_translation':list(root.matrix_world.translation) if root else None,
 'root_parent':root.parent.name if root and root.parent else None,
 'evaluated_mesh_bounds_local':[[min(p[i] for p in all_pts),max(p[i] for p in all_pts)] for i in range(3)],
 'object_names': [o.name for o in objs], 'structural_rectangles':struct,
 'image_or_library_references':image_paths, 'modifier_object_count':sum(len(o.modifiers)>0 for o in objs if o.type=='MESH'),
 'mesh_objects_with_missing_data':sum(o.type=='MESH' and o.data is None for o in objs),
}
Path(out).write_text(json.dumps(metrics,indent=2),encoding='utf-8')
print(out)
print(json.dumps({k:v for k,v in metrics.items() if k not in ('object_names','structural_rectangles')},indent=2))
