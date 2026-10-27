import bpy, json, pathlib, hashlib
p=pathlib.Path(bpy.data.filepath).resolve()
col=bpy.data.collections.get('Asset_massing_house_301837281_58ead22')
scene=bpy.data.scenes.get('Building_massing_house_301837281_58ead22')
root=bpy.data.objects.get('House_301837281')
objs=list(col.all_objects) if col else []
meshes=[o for o in objs if o.type=='MESH']
verts=edges=faces=nonmanifold=boundary=wire=0
for o in meshes:
    me=o.data
    verts+=len(me.vertices); edges+=len(me.edges); faces+=len(me.polygons)
    for e in me.edges:
        linked=0
        for pgn in me.polygons:
            if any(e.key == (min(a,b),max(a,b)) for a,b in zip(pgn.vertices, list(pgn.vertices[1:])+[pgn.vertices[0]])):
                linked+=1
        if linked==0: wire+=1
        if linked==1: boundary+=1
        if linked!=2: nonmanifold+=1
mats={}
for m in bpy.data.materials:
    if not m.use_nodes or not m.node_tree: continue
    types={n.type for n in m.node_tree.nodes}
    if types & {'BSDF_PRINCIPLED'}:
        mats[m.name]=sorted(types)
linked=[]
for lib in bpy.data.libraries:
    path=pathlib.Path(bpy.path.abspath(lib.filepath))
    if not path.exists(): linked.append(str(path))
external=[]
for im in bpy.data.images:
    if im.source=='FILE' and not im.packed_file:
        fp=pathlib.Path(bpy.path.abspath(im.filepath))
        if not fp.exists(): external.append(str(fp))
    if im.packed_file: pass
coords=[tuple(o.matrix_world @ v.co) for o in meshes for v in o.data.vertices]
bounds=[[min(v[i] for v in coords),max(v[i] for v in coords)] for i in range(3)] if coords else None
result={'asset':str(p),'scene':scene.name if scene else None,'collection':col.name if col else None,'root':root.name if root else None,'collection_object_count':len(objs),'mesh_count':len(meshes),'mesh_totals':{'vertices':verts,'edges':edges,'faces':faces,'nonmanifold_edges':nonmanifold,'boundary_edges':boundary,'wire_edges':wire},'bounds_xyz_m':bounds,'material_node_types':mats,'missing_libraries':linked,'external_images_missing':external,'scene_object_names':sorted(o.name for o in bpy.data.objects),'checks':{'scene':bool(scene),'collection':bool(col),'stable_root':bool(root),'no_missing_dependencies':not linked and not external}}
print('FRESH_OPEN_R2='+json.dumps(result,sort_keys=True))
pathlib.Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\phi_gamma_delta\independent_grade_r2\fresh_open_probe.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
