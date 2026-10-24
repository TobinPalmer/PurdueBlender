import bpy,json,os
root=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
path=os.path.join(root,'modular','buildings','native_american_educational_and_cultural_center.blend')
bpy.ops.wm.open_mainfile(filepath=path)
def props(x): return {k:x[k] for k in x.keys()}
asset=bpy.data.collections.get('Asset_native_american_educational_and_cultural_center')
objs=list(asset.all_objects) if asset else []
verts=[]
for o in objs:
 if o.type=='MESH': verts.extend([o.matrix_world@v.co for v in o.data.vertices])
result={'file':path,'collection':asset.name if asset else None,'collection_props':props(asset) if asset else {},'scene_props':props(bpy.context.scene),'objects':len(objs),'first_objects':[{'name':o.name,'type':o.type,'location':list(o.location),'props':props(o)} for o in objs[:8]],'mesh_bounds':[[min(v[i] for v in verts),max(v[i] for v in verts)] for i in range(3)] if verts else None}
print(json.dumps(result,indent=2,default=str))
