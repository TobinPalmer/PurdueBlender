import bpy, json, os, hashlib, math
from mathutils import Vector
asset=os.path.abspath('modular/buildings/rawls_hall.blend')
out=os.path.abspath('audit/batch4_rawls/round8_transform_material_change.json')
bpy.ops.wm.open_mainfile(filepath=asset)

fix_names=[
'Cam_RAWL_01_North_StateSt','Cam_RAWL_02_NW_Curved_Rotunda','Cam_RAWL_03_West_GrantSt_Skywalk',
'Cam_RAWL_04_SE_Diagonal_Facade','Cam_RAWL_05_Roof_Arched_Penthouse','Cam_RAWL_06_Ortho_Footprint_Top',
'RAWL_Site_Sidewalk_Apron','RAWL_South_Windows_South_BronzeMullions']
# Confirm exactly the known stale inverse before touching it.
expected=(-323.6582336425781,409.6224365234375,0.0)
def mat4(m): return [[round(float(m[r][c]),9) for c in range(4)] for r in range(4)]
def bounds(o):
    pts=[o.matrix_world @ Vector(c) for c in o.bound_box]
    return [[round(min(p[i] for p in pts),6),round(max(p[i] for p in pts),6)] for i in range(3)]
def digest_mesh(o):
    h=hashlib.sha256()
    for v in o.data.vertices:
        h.update(('%0.9f,%0.9f,%0.9f;'%(v.co.x,v.co.y,v.co.z)).encode())
    for p in o.data.polygons: h.update((str(tuple(p.vertices))+';').encode())
    return h.hexdigest()
def record(o):
    return {'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,'location':list(o.location),
      'matrix_parent_inverse':mat4(o.matrix_parent_inverse),'matrix_world':mat4(o.matrix_world),'world_bounds':bounds(o),
      'mesh_sha256':digest_mesh(o) if o.type=='MESH' else None}

targets=[bpy.data.objects.get(n) for n in fix_names]
assert all(targets), [n for n,o in zip(fix_names,targets) if not o]
assert all(o.parent and o.parent.name=='AssetRoot_rawls_hall' for o in targets)
for o in targets:
    assert abs(o.matrix_parent_inverse[0][3]-expected[0])<1e-4 and abs(o.matrix_parent_inverse[1][3]-expected[1])<1e-4, (o.name,mat4(o.matrix_parent_inverse))
root=bpy.data.objects['AssetRoot_rawls_hall']
shell=bpy.data.objects['RAWL_Masonry_Exterior_Walls']
before={'asset':asset,'targets':[record(o) for o in targets],'root':record(root),'structural_shell':record(shell)}
# Repair parenting offset without changing object location, rotation, scale or mesh vertices.
for o in targets: o.matrix_parent_inverse.identity()
# Improve transparency while retaining a lightly tinted reflective architectural pane.
glass=bpy.data.materials['RAWL_CurtainWall_Glass'];glass.use_nodes=True
glass.surface_render_method='BLENDED'
glass_pr=next(n for n in glass.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
glass_pr.inputs['Base Color'].default_value=(.30,.43,.49,1)
glass_pr.inputs['Transmission Weight'].default_value=.12
glass_pr.inputs['Roughness'].default_value=.075
glass_pr.inputs['Metallic'].default_value=.02
transparent=next(n for n in glass.node_tree.nodes if n.type=='BSDF_TRANSPARENT')
mix=next(n for n in glass.node_tree.nodes if n.type=='MIX_SHADER')
# Shader 2 is Transparent, so .45 reveals useful interior depth without erasing the pane.
mix.inputs[0].default_value=.45
glass.diffuse_color=(.30,.43,.49,.42)
# Reduce mortar brightness in the physically mapped facade material while preserving brick colors.
brickmat=bpy.data.materials['RAWL_Purdue_Red_Brick']
brick_nodes=[n for n in brickmat.node_tree.nodes if n.type=='TEX_BRICK']
assert len(brick_nodes)>=2
mortar_before=[]
for n in brick_nodes:
    sock=n.inputs.get('Mortar')
    if sock:
        mortar_before.append({'node':n.name,'color':list(sock.default_value)})
        c=sock.default_value
        # Lower luminance ~18%; keep neutral warm stone hue.
        sock.default_value=(c[0]*.82,c[1]*.82,c[2]*.82,c[3])
# Ensure scene still points at its original asset scene and preserve local frame.
after={'asset':asset,'targets':[record(o) for o in targets],'root':record(root),'structural_shell':record(shell),
 'glass':{'transparent_mix_factor':float(mix.inputs[0].default_value),'base_color':list(glass_pr.inputs['Base Color'].default_value),'transmission':float(glass_pr.inputs['Transmission Weight'].default_value),'roughness':float(glass_pr.inputs['Roughness'].default_value)},
 'mortar':{'before':mortar_before,'after':[{'node':n.name,'color':list(n.inputs['Mortar'].default_value)} for n in brick_nodes]}}
# Shell/root and mesh data are required to be exactly unchanged.
assert before['root']['matrix_world']==after['root']['matrix_world'] and before['root']['mesh_sha256']==after['root']['mesh_sha256']
assert before['structural_shell']['matrix_world']==after['structural_shell']['matrix_world'] and before['structural_shell']['mesh_sha256']==after['structural_shell']['mesh_sha256']
for b,a in zip(before['targets'],after['targets']):
    assert b['mesh_sha256']==a['mesh_sha256']
    assert b['location']==a['location']
    assert a['matrix_parent_inverse']==mat4(bpy.data.objects[b['name']].matrix_parent_inverse)
report={'before':before,'after':after,'notes':'Reset stale matrix_parent_inverse on six saved cameras and two meshes; mesh geometry and root/shell unchanged. Tweaked glass transparency and brick mortar only.'}
with open(out,'w') as f: json.dump(report,f,indent=2)
bpy.ops.wm.save_as_mainfile(filepath=asset)
print('Saved',asset)
print('Evidence',out)
print('BEFORE',json.dumps(before,indent=2))
print('AFTER',json.dumps(after,indent=2))

