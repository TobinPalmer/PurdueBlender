import bpy,json
names=['mansard','dormer','tower','cupola','spire','finial','roof','steeple']
items=[]
for o in bpy.data.objects:
    if not any(k in o.name.lower() for k in names):continue
    items.append({'name':o.name,'type':o.type,'hide_render':o.hide_render,'hide_viewport':o.hide_viewport,'hide_get':o.hide_get(),'location':list(o.location),'dimensions':list(o.dimensions),'parent':o.parent.name if o.parent else None,'collections':[c.name for c in o.users_collection],'materials':[m.name if m else None for m in o.data.materials] if o.type=='MESH' else []})
print(json.dumps(items,indent=2))
