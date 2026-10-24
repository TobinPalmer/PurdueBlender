import bpy, json
p=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/knoy_hall.blend'
bpy.ops.wm.open_mainfile(filepath=p)
asset=bpy.data.collections.get('Asset_knoy_hall')
objs=list(asset.all_objects) if asset else []
rows=[]
for o in objs:
    if any(k in o.name.lower() for k in ['solar','photovolta','cool','tower','penthouse','roof','slab_l']):
        rows.append({'name':o.name,'type':o.type,'verts':len(o.data.vertices) if o.type=='MESH' else 0,'dims':list(o.dimensions),'loc':list(o.location),'bounds':[[min((o.matrix_world@__import__('mathutils').Vector(v))[i] for v in o.bound_box) for i in range(3)],[max((o.matrix_world@__import__('mathutils').Vector(v))[i] for v in o.bound_box) for i in range(3)]] if o.type=='MESH' else None})
print(json.dumps({'asset_count':len(objs),'matches':rows},indent=2))
