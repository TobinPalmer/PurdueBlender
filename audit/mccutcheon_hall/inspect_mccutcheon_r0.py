import bpy, os, json
from mathutils import Vector

ROOT=os.path.abspath('.')
ASSET=os.path.join(ROOT,'modular','buildings','mccutcheon_hall.blend')
bpy.ops.wm.open_mainfile(filepath=ASSET)
coll=bpy.data.collections.get('Asset_mccutcheon_hall')
assert coll
rows=[]
for o in coll.all_objects:
    pts=[o.matrix_world@Vector(c) for c in o.bound_box] if o.type in {'MESH','CURVE','FONT','SURFACE','META'} else []
    bounds=None
    if pts:
        bounds=[[round(min(p[i] for p in pts),4),round(max(p[i] for p in pts),4)] for i in range(3)]
    mats=[]
    if getattr(o.data,'materials',None): mats=[m.name if m else None for m in o.data.materials]
    rows.append({'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,
                 'location':[round(float(x),4) for x in o.location],
                 'rotation':[round(float(x),5) for x in o.rotation_euler],
                 'scale':[round(float(x),5) for x in o.scale],
                 'world_bounds_m':bounds,'materials':mats,
                 'hide_render':o.hide_render,'hide_viewport':o.hide_viewport})
materials=[]
for m in bpy.data.materials:
    if not m.use_nodes: materials.append({'name':m.name,'use_nodes':False}); continue
    nodes=[]
    for n in m.node_tree.nodes:
        entry={'name':n.name,'type':n.type}
        if n.type=='BSDF_PRINCIPLED':
            entry['base_color']=[round(float(x),4) for x in n.inputs['Base Color'].default_value]
            entry['roughness']=round(float(n.inputs['Roughness'].default_value),4)
            entry['metallic']=round(float(n.inputs['Metallic'].default_value),4)
        nodes.append(entry)
    materials.append({'name':m.name,'nodes':nodes,
      'links':[{'from':l.from_node.name,'to':l.to_node.name,'socket':l.to_socket.name} for l in m.node_tree.links]})
report={'asset':ASSET,'collection':coll.name,'collection_object_count':len(coll.all_objects),
        'direct_object_count':len(coll.objects),'scenes':[s.name for s in bpy.data.scenes],
        'collection_objects':rows,'materials':materials}
out=os.path.join(ROOT,'audit','mccutcheon_hall','mccutcheon_r0_inspection.json')
with open(out,'w',encoding='utf-8') as f: json.dump(report,f,indent=2)
print('objects',len(rows),'materials',len(materials),'wrote',out)
