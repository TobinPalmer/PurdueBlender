"""Reopen and verify the standalone Lyles-Porter Hall source library."""
import bpy, json, os
from mathutils import Vector

root=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..'))
blend=os.path.join(root,'modular','buildings','lyles_porter_hall.blend')
bpy.ops.wm.open_mainfile(filepath=blend)
col=bpy.data.collections.get('Asset_lyles_porter_hall')
assert col is not None
objects=list(col.all_objects)
assert objects, 'export collection is empty'
meshes=[o for o in objects if o.type=='MESH']
depsgraph=bpy.context.evaluated_depsgraph_get()
corners=[]
for o in objects:
    if o.type not in {'MESH','CURVE','FONT'}: continue
    ev=o.evaluated_get(depsgraph)
    for p in ev.bound_box:
        corners.append(ev.matrix_world @ Vector(p))
bounds=[[min(v[i] for v in corners),max(v[i] for v in corners)] for i in range(3)]
mats={m for o in objects for m in getattr(o.data,'materials',[]) if m}
texture_materials=[]
for m in mats:
    if not m.use_nodes or not m.node_tree: continue
    nodes=m.node_tree.nodes
    connected=any(n.bl_idname in {'ShaderNodeTexNoise','ShaderNodeTexBrick','ShaderNodeTexImage','ShaderNodeTexVoronoi'} and any(o.is_linked for o in n.outputs) for n in nodes)
    if connected: texture_materials.append(m.name)
asset_obj_names=[o.name for o in objects]
merged_source_names=' '.join(o.get('merged_source_names','') for o in objects)
assert 'punched windows' in merged_source_names, 'punched shell missing'
assert 'sound booth' in merged_source_names, 'audiology interior cue missing'
assert bounds[0][1]-bounds[0][0] > 80 and bounds[1][1]-bounds[1][0] > 55
result={
  'blend_path':blend,'reopened':True,'collection':'Asset_lyles_porter_hall',
  'objects':len(objects),'mesh_objects':len(meshes),'materials':len(mats),
  'texture_connected_material_count':len(texture_materials),'texture_materials':sorted(texture_materials),
  'local_bounds_m':bounds,'library_external_image_paths':[im.filepath for im in bpy.data.images if im.source=='FILE'],
  'placement_origin_campus_xy_m':[-257.675,-717.457],
  'preview_images':['audit/lyles_porter_hall/lyles_porter_hall_preview.png','audit/lyles_porter_hall/lyles_porter_hall_entry_detail.png']
}
out=os.path.join(os.path.dirname(__file__),'verification.json')
with open(out,'w',encoding='utf-8') as f: json.dump(result,f,indent=2)
print('LPH_REOPEN_VERIFY',json.dumps(result))
