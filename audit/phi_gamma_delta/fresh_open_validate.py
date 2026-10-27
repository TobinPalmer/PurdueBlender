import bpy, json, os, hashlib, bmesh

path=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\massing_house_301837281_58ead22.blend'
bpy.ops.wm.open_mainfile(filepath=path)
scene=bpy.data.scenes.get('Building_massing_house_301837281_58ead22')
col=bpy.data.collections.get('Asset_massing_house_301837281_58ead22')
root=bpy.data.objects.get('House_301837281')
assert scene is not None and col is not None and root is not None
assert root.type=='MESH'
assert all(o.name in bpy.data.objects for o in col.objects)
assert bpy.data.objects.get('Original_House_West_Hipped_Slate_Roof') is not None
assert bpy.data.objects.get('Original_House_South_Hipped_Slate_Roof') is not None
assert bpy.data.objects.get('Lyles_Addition_Low_Hipped_Slate_Roof') is not None
assert bpy.data.objects.get('Lyles_Addition_Arched_Glazing') is not None
assert not any(o.name.startswith('PhiGam_') and o.type in {'CAMERA','LIGHT'} for o in bpy.data.objects)
world_bounds=[]
for axis in range(3):
    vals=[]
    for ob in col.objects:
        for v in ob.bound_box:
            vals.append((ob.matrix_world @ __import__('mathutils').Vector(v))[axis])
    world_bounds.append([round(min(vals),5),round(max(vals),5)])
assert world_bounds[0][0] < -443 and world_bounds[0][1] > -418
assert world_bounds[1][0] < 398 and world_bounds[1][1] > 423
assert world_bounds[2][0] <= 0 and 11.5 < world_bounds[2][1] < 12.5
missing=[]
for image in bpy.data.images:
    if image.source=='FILE' and image.filepath and not image.packed_file:
        p=bpy.path.abspath(image.filepath)
        if not os.path.exists(p): missing.append(image.filepath)
assert not missing, missing
topology={'mesh_objects':0,'edges':0,'boundary_edges':0,'nonmanifold_edges':0,'wire_edges':0}
for ob in col.all_objects:
    if ob.type!='MESH': continue
    topology['mesh_objects']+=1
    bm=bmesh.new(); bm.from_mesh(ob.data); bm.normal_update()
    topology['edges']+=len(bm.edges)
    topology['boundary_edges']+=sum(e.is_boundary for e in bm.edges)
    topology['nonmanifold_edges']+=sum(not e.is_manifold for e in bm.edges)
    topology['wire_edges']+=sum(not e.link_faces for e in bm.edges)
    bm.free()
assert topology['boundary_edges']==0 and topology['nonmanifold_edges']==0 and topology['wire_edges']==0,topology
assert any(n.type=='TEX_BRICK' for n in bpy.data.materials['PhiGam_Buff_Tan_Brick'].node_tree.nodes)
assert any(n.type=='TEX_NOISE' for n in bpy.data.materials['PhiGam_Weathered_Slate'].node_tree.nodes)
with open(path,'rb') as f: sha=hashlib.sha256(f.read()).hexdigest().upper()
report={'status':'PASS','asset':path,'sha256':sha,'scene':scene.name,'collection':col.name,
        'stable_root_object':root.name,'collection_object_count':len(col.objects),
        'bounds_xyz_m':world_bounds,'external_unpacked_images':missing,'topology':topology,
        'checks':['fresh process open','expected scene, collection and root object','roof and brick details exist',
                  'temporary camera/light removed','GIS XY extent retained','estimated ridge height present',
                  'no missing external images','all mesh edges manifold with no boundary or wire edges',
                  'procedural brick/slate materials load']}
out=r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\phi_gamma_delta\fresh_open_validation.json'
with open(out,'w',encoding='utf-8') as f: json.dump(report,f,indent=2)
print('FRESH_OPEN_VALIDATION',json.dumps(report))
