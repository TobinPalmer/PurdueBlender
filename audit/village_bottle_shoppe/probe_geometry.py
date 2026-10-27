import bpy, json
obj=bpy.data.objects.get('Village Bottle Shoppe')
print('VERTS='+json.dumps([list(v.co) for v in obj.data.vertices]))
print('POLYS='+json.dumps([{'verts':list(p.vertices),'material':p.material_index,'normal':list(p.normal)} for p in obj.data.polygons]))
