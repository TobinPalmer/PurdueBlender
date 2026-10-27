import bpy, json, math, hashlib, os
from pathlib import Path
blend = Path(r'modular/buildings/massing_phi_kappa_tau_139b9d7.blend').resolve()
assert bpy.ops.wm.open_mainfile(filepath=str(blend)) == {'FINISHED'}
scene_name='Building_massing_phi_kappa_tau_139b9d7'
collection_name='Asset_massing_phi_kappa_tau_139b9d7'
scene=bpy.data.scenes.get(scene_name)
coll=bpy.data.collections.get(collection_name)
objs=list(coll.objects) if coll else []
obj=next((o for o in objs if o.name=='Phi Kappa Tau'),None)
assert scene and coll and obj and obj.type=='MESH'
mesh=obj.data
bm=None
# Exact saved mesh topology and portable image-path evidence.
edge_by_key={tuple(sorted(e.vertices)):e.index for e in mesh.edges}
edge_uses={e.index:0 for e in mesh.edges}
for p in mesh.polygons:
    for key in p.edge_keys:
        edge_uses[edge_by_key[tuple(sorted(key))]]+=1
nonmanifold=sum(1 for n in edge_uses.values() if n!=2)
loose=sum(1 for n in edge_uses.values() if n==0)
coords=[obj.matrix_world @ v.co for v in mesh.vertices]
bounds=[[min(v[i] for v in coords),max(v[i] for v in coords)] for i in range(3)]
# Wall footprint ring encoded on the mesh data, independent check of raw GIS ring vertices at foundation top.
ring=json.loads(obj.get('gis_wall_ring_xy_m_json','[]'))
verts=[(obj.matrix_world @ v.co) for v in mesh.vertices]
level=[v for v in verts if abs(v.z-0.78)<1e-5]
nearest=[min(math.dist((v.x,v.y),p) for v in level) for p in ring]
paths=[]
for image in bpy.data.images:
    if image.source=='FILE':
        paths.append({'name':image.name,'path':image.filepath,'exists':Path(bpy.path.abspath(image.filepath,library=image.library)).exists() if image.filepath else False})
report={'independent_fresh_reopen':True,'blender_version':bpy.app.version_string,'scene_names':[s.name for s in bpy.data.scenes], 'scene_ok':bool(scene),'collection_ok':bool(coll),'collection_object_names':[o.name for o in objs],'object_count':len(objs),'object_type':obj.type,'asset_id':obj.get('asset_id'),'source_feature':obj.get('source_feature'),'object_transform':{'location':list(obj.location),'rotation_euler':list(obj.rotation_euler),'scale':list(obj.scale)},'vertex_count':len(mesh.vertices),'edge_count':len(mesh.edges),'face_count':len(mesh.polygons),'nonmanifold_edges':nonmanifold,'loose_edges':loose,'world_bounds_m':bounds,'materials':sorted({m.name for m in mesh.materials if m}),'external_images':paths,'stored_footprint_ring_vertex_count':len(ring),'foundation_vertices_at_z_0_78':len(level),'fid820_ring_max_nearest_error_m':max(nearest) if nearest else None}
print(json.dumps(report,indent=2))

