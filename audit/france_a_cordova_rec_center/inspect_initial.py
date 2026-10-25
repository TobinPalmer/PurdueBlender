import bpy, json
for o in bpy.data.objects:
    if o.type=='MESH':
        world=[o.matrix_world @ __import__('mathutils').Vector(c) for c in o.bound_box]
        bb=[[min(v[i] for v in world),max(v[i] for v in world)] for i in range(3)]
        print(json.dumps({'name':o.name,'type':o.type,'vertices':len(o.data.vertices),'faces':len(o.data.polygons),'bounds':bb,'materials':[m.name if m else None for m in o.data.materials]}))
print('COLLECTIONS',[(c.name,len(c.all_objects)) for c in bpy.data.collections])
