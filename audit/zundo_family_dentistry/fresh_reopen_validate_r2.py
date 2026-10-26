import bpy, json, os
from mathutils import Vector
root=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..'))
path=os.path.join(root,'modular','buildings','zundo_family_dentistry_r2.blend')
bpy.ops.wm.open_mainfile(filepath=path)
name='Asset_massing_zundo_family_dentistry_f840e2b'
col=bpy.data.collections.get(name)
assert col is not None, 'stable asset/export collection missing'
assert len(col.objects)>200, 'detailed R2 export collection unexpectedly sparse'
assert bpy.data.objects.get('Street entry glazed door') is not None
assert bpy.data.objects.get('Practice sign panel') is not None
assert bpy.data.objects.get('Zundo Family Dentistry sign lettering') is not None
assert bpy.data.objects.get('Operatory door leaf') is not None
assert bpy.data.objects.get('Operatory upper cabinet 0') is not None
assert bpy.data.objects.get('Operatory ceiling task panel 0') is not None
assert not any(o.name.startswith('Preview tree') for o in col.objects), 'preview trees leaked into export collection'
assert bpy.data.collections.get('Preview_only_site_context_exclude_from_master') is not None
pts=[]
for o in col.objects:
 if o.type=='MESH':pts += [o.matrix_world@v.co for v in o.data.vertices]
mins=[min(v[i] for v in pts) for i in range(3)];maxs=[max(v[i] for v in pts) for i in range(3)]
missing=[]
for m in bpy.data.materials:
 if m.users and m.use_nodes:
  for n in m.node_tree.nodes:
   if n.type=='TEX_IMAGE' and n.image and n.image.source=='FILE' and not n.image.packed_file and not os.path.exists(bpy.path.abspath(n.image.filepath)):missing.append(n.image.filepath)
assert not missing, 'missing external files: '+str(missing)
types={}
for o in col.objects:types[o.type]=types.get(o.type,0)+1
report={'fresh_reopen':'pass','file':os.path.relpath(path,root).replace('\\','/'),'scene':bpy.context.scene.name,'export_collection':name,'export_object_count':len(col.objects),'object_types':types,'materials_assigned_to_export_objects':len({m.name for o in col.objects for m in o.data.materials if m}),'materials_used_in_file':len([m for m in bpy.data.materials if m.users>0]),'local_bounds_with_entry_site_elements_m':[[round(mins[i],4),round(maxs[i],4)] for i in range(3)],'preview_trees_inside_export_collection':False,'unpacked_missing_external_textures':missing,'renders':['zundo_r2_front.png','zundo_r2_side_rear.png','zundo_r2_roof_off.png']}
with open(os.path.join(os.path.dirname(__file__),'fresh_reopen_validation_r2.json'),'w') as f:json.dump(report,f,indent=2)
print('R2_REOPEN_VALIDATION',json.dumps(report))
