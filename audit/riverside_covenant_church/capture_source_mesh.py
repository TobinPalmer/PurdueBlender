import bpy,json,os
cfg=json.load(open(os.path.join(os.path.dirname(__file__),'build_config.json'),encoding='utf-8-sig'))
obj=bpy.data.objects[cfg['object_name']]
mesh=obj.data
out={'asset_id':cfg['asset_id'],'object':obj.name,'object_location':list(obj.location),'rotation_euler':list(obj.rotation_euler),'scale':list(obj.scale),'vertex_count':len(mesh.vertices),'face_count':len(mesh.polygons),'materials':[m.name if m else None for m in mesh.materials],'vertices_local':[list(v.co) for v in mesh.vertices],'faces':[list(p.vertices) for p in mesh.polygons]}
world=[obj.matrix_world @ v.co for v in mesh.vertices]
out['bounds_world_m']=[[min(v[i] for v in world),max(v[i] for v in world)] for i in range(3)]
with open(os.path.join(os.path.dirname(__file__),'source_mesh_snapshot.json'),'w',encoding='utf8') as f: json.dump(out,f,indent=2)
print('SOURCE_MESH_JSON='+json.dumps({k:out[k] for k in ('asset_id','vertex_count','face_count','bounds_world_m','materials')}))
