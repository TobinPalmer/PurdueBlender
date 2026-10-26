import bpy, json, os, hashlib
from mathutils import Vector
root=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..'))
path=os.path.join(root,'modular','buildings','zundo_family_dentistry.blend')
bpy.ops.wm.open_mainfile(filepath=path)
name='Asset_massing_zundo_family_dentistry_f840e2b'
col=bpy.data.collections.get(name)
assert col is not None, 'stable export collection missing'
assert len(col.objects)>100, 'detailed geometry unexpectedly missing'
assert all(o.type=='MESH' for o in col.objects if o.type in {'MESH','CURVE'}), 'unexpected geometry type'
pts=[]
for o in col.objects:
 if o.type=='MESH':
  for v in o.data.vertices:pts.append(o.matrix_world@v.co)
mins=[min(p[i] for p in pts) for i in range(3)];maxs=[max(p[i] for p in pts) for i in range(3)]
missing=[]
for m in bpy.data.materials:
 if m.users and m.use_nodes:
  for n in m.node_tree.nodes:
   if n.type=='TEX_IMAGE' and n.image and n.image.source=='FILE' and not n.image.packed_file:
    if not os.path.exists(bpy.path.abspath(n.image.filepath)):missing.append(n.image.filepath)
assert not missing, 'missing unpacked texture dependencies: '+str(missing)
report={'fresh_reopen':'pass','file':os.path.relpath(path,root).replace('\\','/'),'scene':bpy.context.scene.name,'export_collection':name,'export_collection_object_count':len(col.objects),'mesh_count':sum(o.type=='MESH' for o in col.objects),'materials_used_by_export_objects':len({m.name for o in col.objects for m in o.data.materials if m}) ,'local_bounds_m':[[round(mins[i],4),round(maxs[i],4)] for i in range(3)],'unpacked_external_texture_dependencies':missing}
with open(os.path.join(os.path.dirname(__file__),'fresh_reopen_validation.json'),'w') as f:json.dump(report,f,indent=2)
print('FRESH_REOPEN',json.dumps(report))
