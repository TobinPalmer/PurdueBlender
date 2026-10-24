import bpy, json
p=r'modular/buildings/massing_birck_nanotechnology_center_362d0b7.blend'
bpy.ops.wm.open_mainfile(filepath=p)
res=[]
for o in bpy.context.scene.objects:
    if o.type=='MESH':
        co=[o.matrix_world @ v.co for v in o.data.vertices]
        res.append({'name':o.name,'loc':list(o.location),'dims':list(o.dimensions),'verts':len(o.data.vertices),'polys':len(o.data.polygons),'materials':[m.name if m else None for m in o.data.materials], 'min':[min(v[i] for v in co) for i in range(3)], 'max':[max(v[i] for v in co) for i in range(3)]})
print(json.dumps({'file':bpy.data.filepath,'objs':res},indent=2))
