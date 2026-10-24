import bpy, json
from pathlib import Path

out = {}
asset = bpy.data.collections.get('Asset_mechanical_engineering')
out['scene'] = bpy.context.scene.name if bpy.context.scene else None
out['asset_collection_found'] = asset is not None
out['asset_name'] = asset.name if asset else None
out['direct_objects'] = len(asset.objects) if asset else None
objects = []
for ob in (asset.all_objects if asset else bpy.data.objects):
    item = {
        'name': ob.name,
        'type': ob.type,
        'location': [round(float(x), 4) for x in ob.location],
        'rotation_euler': [round(float(x), 5) for x in ob.rotation_euler],
        'scale': [round(float(x), 5) for x in ob.scale],
        'parent': ob.parent.name if ob.parent else None,
        'collections': [c.name for c in ob.users_collection],
        'materials': [m.name if m else None for m in ob.data.materials] if ob.type == 'MESH' else [],
        'modifiers': [{'name': m.name, 'type': m.type, 'show_render': m.show_render} for m in ob.modifiers],
    }
    if ob.type == 'MESH':
        corners = [ob.matrix_world @ __import__('mathutils').Vector(c) for c in ob.bound_box]
        item['bounds_world'] = [[round(min(v[i] for v in corners), 4), round(max(v[i] for v in corners), 4)] for i in range(3)]
        item['vertices'] = len(ob.data.vertices)
        item['faces'] = len(ob.data.polygons)
    item['custom'] = {k: str(ob[k]) for k in ob.keys() if k != '_RNA_UI'}
    objects.append(item)
out['objects'] = objects
out['materials'] = []
for mat in bpy.data.materials:
    if mat.users == 0: continue
    info = {'name': mat.name, 'users': mat.users, 'nodes': mat.use_nodes}
    if mat.use_nodes:
        info['node_types'] = [n.bl_idname for n in mat.node_tree.nodes]
        info['images'] = [n.image.filepath for n in mat.node_tree.nodes if n.type == 'TEX_IMAGE' and n.image]
    out['materials'].append(info)
if asset:
    allv=[]
    for ob in asset.all_objects:
        if ob.type=='MESH': allv.extend(ob.matrix_world @ __import__('mathutils').Vector(c) for c in ob.bound_box)
    if allv: out['asset_bounds_world']=[[round(min(v[i] for v in allv),4),round(max(v[i] for v in allv),4)] for i in range(3)]
Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/audit/complete_me/inspection_r0.json').write_text(json.dumps(out,indent=2))
