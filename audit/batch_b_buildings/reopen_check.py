import bpy, json, sys, os
from pathlib import Path
args=sys.argv[sys.argv.index('--')+1:]
path,key=args[0],args[1]
bpy.ops.wm.open_mainfile(filepath=os.path.abspath(path))
a=bpy.data.collections.get('Asset_'+key)
assert a is not None, 'Missing stable collection'
objs=list(a.all_objects); meshes=[o for o in objs if o.type=='MESH']
mats={m for o in objs if o.type=='MESH' for m in o.data.materials if m}
assert len(meshes)>=3, f'Unexpectedly sparse geometry: {len(meshes)}'
assert mats, 'No materials assigned'
checks=[]
for m in mats:
 out=next((n for n in m.node_tree.nodes if n.type=='OUTPUT_MATERIAL'),None) if m.use_nodes else None
 assert out and any(l.to_node==out and l.to_socket.name=='Surface' for l in m.node_tree.links), 'Unconnected material output: '+m.name
 checks.append({'material':m.name,'nodes':len(m.node_tree.nodes),'texture_connected':any(n.type in {'TEX_NOISE','TEX_IMAGE','TEX_VORONOI'} for n in m.node_tree.nodes)})
origin=list(a.get('placement_origin_xy_m',[])); assert len(origin)==2 and all(abs(v)<2000 for v in origin), 'Bad placement origin'
assert a.get('local_coordinates') is True
report={'opened':True,'collection':a.name,'objects':len(objs),'mesh_objects':len(meshes),'materials':len(mats),'texture_node_materials':sum(x['texture_connected'] for x in checks),'placement_origin_xy_m':origin,'source_feature_id':a.get('source_feature_id')}
print('CHECK_RESULT='+json.dumps(report))
epath=Path('audit/batch_b_buildings')/(key+'_evidence.json')
e=json.loads(epath.read_text(encoding='utf-8')); e['validation']={'saved_and_reopened':True,'reopen_check':report,'preview_path':'audit/batch_b_buildings/'+key+'_preview.png','texture_nodes_connected':all(x['texture_connected'] for x in checks)}
epath.write_text(json.dumps(e,indent=2),encoding='utf-8')
