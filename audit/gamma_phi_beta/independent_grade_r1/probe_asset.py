import bpy, json, hashlib, os
p = bpy.data.filepath
coll = bpy.data.collections.get('Asset_gamma_phi_beta')
objs = list(coll.all_objects) if coll else []
meshobjs = [o for o in objs if o.type == 'MESH']
materials = {}
for o in meshobjs:
    for m in o.data.materials:
        if m:
            materials[m.name] = materials.get(m.name, 0) + 1
result = {
 'blend_path':p,
 'sha256':hashlib.sha256(open(p,'rb').read()).hexdigest(),
 'scenes':[s.name for s in bpy.data.scenes],
 'collections':[c.name for c in bpy.data.collections],
 'target_collection':coll.name if coll else None,
 'object_count':len(objs),
 'mesh_count':len(meshobjs),
 'materials_by_mesh_assignment':materials,
 'named_objects':[o.name for o in objs],
 'non_mesh_objects':[(o.name,o.type) for o in objs if o.type!='MESH'],
 'externals':[i.filepath for i in bpy.data.images if i.source=='FILE' and not i.packed_file],
 'mesh_local_bounds':None,
}
if objs:
    from mathutils import Vector
    coords=[]
    for o in objs:
        if o.type=='MESH':
            coords += [o.matrix_world @ Vector(c) for c in o.bound_box]
    if coords:
        result['mesh_world_bounds']=[[min(v[i] for v in coords), max(v[i] for v in coords)] for i in range(3)]
open(r'audit/gamma_phi_beta/independent_grade_r1/asset_probe.json','w').write(json.dumps(result,indent=2))
