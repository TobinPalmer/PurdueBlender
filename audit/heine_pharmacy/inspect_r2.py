import bpy,json
bpy.ops.wm.open_mainfile(filepath='modular/buildings/heine_pharmacy.blend')
c=bpy.data.collections['Asset_heine_pharmacy']
out=[]
for o in c.all_objects:
 if any(k in o.name.lower() for k in ['arcade','arch','entry','portal','window stacks','limestone window','mullion']):
  b=[list(o.matrix_world@__import__('mathutils').Vector(v)) for v in o.bound_box]
  out.append({'name':o.name,'type':o.type,'location':list(o.location),'dims':list(o.dimensions),'bounds':[[min(v[i] for v in b),max(v[i] for v in b)] for i in range(3)],'verts':len(o.data.vertices) if o.type=='MESH' else None,'polys':len(o.data.polygons) if o.type=='MESH' else None})
print(json.dumps(out,indent=2))
