import bpy, bmesh, json, math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
ID='massing_cary_quadrangle_west_cqw_3d47a7d'
COL=f'Asset_{ID}'; SCENE=f'Building_{ID}'
coll=bpy.data.collections.get(COL)
if bpy.context.scene.name != SCENE or coll is None: raise RuntimeError('Missing expected scene/collection')
objs=list(coll.objects); meshes=[o for o in objs if o.type=='MESH']
dg=bpy.context.evaluated_depsgraph_get(); points=[]
mods={}
for obj in meshes:
    for m in obj.modifiers: mods[m.type]=mods.get(m.type,0)+1
    ev=obj.evaluated_get(dg)
    points.extend(ev.matrix_world @ Vector(c) for c in ev.bound_box)
bounds=[[min(p[i] for p in points),max(p[i] for p in points)] for i in range(3)]
shell=bpy.data.objects.get('Cary Quadrangle West (CQW) shell')
if shell is None or shell.name not in coll.objects: raise RuntimeError('Footprint shell absent from exported collection')
sverts=[shell.matrix_world @ v.co for v in shell.data.vertices]
shell_bounds=[[min(v[i] for v in sverts),max(v[i] for v in sverts)] for i in range(2)]
bm=bmesh.new(); bm.from_mesh(shell.data)
topo={'nonmanifold':sum(not e.is_manifold for e in bm.edges),'boundary':sum(e.is_boundary for e in bm.edges)}; bm.free()
# External dependencies are recorded so portability can be checked explicitly.
external=[]
for block in bpy.data.images:
    if block.source=='FILE' and block.filepath:
        path=bpy.path.abspath(block.filepath)
        if not Path(path).exists(): external.append({'type':'image','path':block.filepath,'resolved':path,'exists':False})
for lib in bpy.data.libraries:
    p=bpy.path.abspath(lib.filepath)
    external.append({'type':'library','path':lib.filepath,'resolved':p,'exists':Path(p).exists()})
# Save a fresh render from the reopened saved scene if its camera is configured.
render_path=Path(__file__).resolve().parent/'fresh_reopen_render.png'
scene=bpy.context.scene; scene.render.resolution_percentage=70; scene.render.filepath=str(render_path)
if scene.camera: bpy.ops.render.render(write_still=True)
result={'blender_version':bpy.app.version_string,'asset_path':f'modular/buildings/{ID}.blend','scene':scene.name,'collection':COL,'collection_present':coll is not None,'object_count':len(objs),'mesh_count':len(meshes),'evaluated_bounds_m':bounds,'shell_name':shell.name,'shell_vertex_count':len(shell.data.vertices),'shell_xy_bounds_m':shell_bounds,'shell_topology':topo,'modifiers':mods,'external_dependencies':external,'fresh_render':str(render_path.relative_to(ROOT)).replace('\\','/') if scene.camera else None}
(Path(__file__).resolve().parent/'blender_probe.json').write_text(json.dumps(result,indent=2),encoding='utf8')
print(json.dumps(result,indent=2))

